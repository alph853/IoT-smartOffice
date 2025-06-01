import os
import json
from PIL import Image
import io
import subprocess
import threading
import atexit
import signal
from datetime import datetime
from thingsboard import GW_ROOT
from .retrieval import TagRetrieval, ClipRetrieval
import imagehash
import base64


class AIService:
    def __init__(self,
                 image_save_dir="images",
                 batch_size=16,
                 timeout_seconds=30,
                 ):

        # IMAGE setup
        self.image_save_dir = os.path.join(GW_ROOT, "services", image_save_dir)
        self.global_image_idx = 0
        self.image_metadata = {}
        self.prev_image = None
        os.makedirs(self.image_save_dir, exist_ok=True)
        self._load_metadata()

        # PROCESSING setup
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.queued_images = []

        self.lock = threading.Lock()
        self.processing_lock = threading.Lock()
        self.processor_event = threading.Event()

        # RETRIEVAL setup
        self.tag_retrieval = TagRetrieval(root_dir=GW_ROOT)
        self.clip_retrieval = ClipRetrieval(root_dir=GW_ROOT)

        # Register shutdown handlers
        atexit.register(self.shutdown)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def start_inference(self, publisher):
        self.msg_publisher = publisher
        threading.Thread(target=self._processor, daemon=True).start()

    def search(self, nl_query: str = None, tag_query: str = None, k=10):
        """
        Search for images based on natural language query and/or tag query.
        """
        scores, top_k_indices = [], []
        if nl_query:
            score, top_k_index = self.clip_retrieval.search(nl_query, k)
            scores.append(score)
            top_k_indices.append(top_k_index)

        if tag_query:
            score, top_k_index = self.tag_retrieval.search(tag_query, k)
            scores.append(score)
            top_k_indices.append(top_k_index)

        if len(scores) == 1:
            scores = scores[0]
            top_k_indices = top_k_indices[0]
        else:
            pass

        filenames = list(map(lambda x: self.image_metadata[x]["filename"], top_k_indices))

        return scores, filenames

    def save_captured_image(self, image_data):
        """save captured image to disk and add to processing queue
        """
        image = Image.open(io.BytesIO(image_data))
        if self.prev_image is not None:
            # find distance between prev_image and current image using hash
            distance = imagehash.phash(self.prev_image) - imagehash.phash(image)
            if distance < 5:
                return None
        self.prev_image = image

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond // 1000:02d}"
        filename = f"{timestamp}.jpg"
        filepath = os.path.join(self.image_save_dir, filename)

        self.image_metadata[self.global_image_idx] = {
            "filename": filename,
        }
        self.global_image_idx += 1

        with open(filepath, 'wb') as f:
            f.write(image_data)

        self.msg_publisher({
            "image": {
                "filename": filename,
                "image_data": base64.b64encode(image_data).decode("utf-8"),
            }
        })

        with self.lock:
            self.queued_images.append(filepath)

        if len(self.queued_images) >= self.batch_size:
            self.processor_event.set()

        return filepath

    def _processor(self):
        """a deamon thread that processes batches of images when ready
        There are two waits, meaning the maximum waiting time is 2*timeout, and minimum is timeout.
        """
        while True:
            # self.processor_event.wait(self.timeout_seconds)
            self.processor_event.wait(self.timeout_seconds)

            with self.lock:
                batch = self.queued_images
                self.queued_images = []

            if batch and self.processing_lock.acquire(blocking=False):
                self._batch_inference(batch)
                self.processing_lock.release()

    def _batch_inference(self, image_paths):
        """Run inference on a batch of images using a subprocess.
        """
        if not image_paths:
            return

        try:
            contexts = ["tag"]
            child_path = os.path.join(GW_ROOT, "services", "inference", "inference.py")
            child_processor = subprocess.Popen(
                ["python", child_path, "--image_paths"] + image_paths + ["--contexts"] + contexts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            o, e = child_processor.communicate()

            if child_processor.returncode != 0:
                print(f"Inference process failed: {e}")
                return

            results = json.loads(o)

            if results.get("tag", None) is not None:
                tag_outputs, tag_contexts = results["tag"]
                msg = {"tags": {
                    "filenames": [os.path.basename(p) for p in image_paths],
                    "outputs": tag_outputs,
                }
                }
                self.msg_publisher(msg)
                self.tag_retrieval.add_contexts(tag_contexts)

                # save to disk after processing batches
                self._save_metadata()

            elif results.get("clip", None) is not None:
                # Handle clip results if needed
                pass

            print("save batches successfully")
        except Exception as e:
            print(f"Error during batch inference: {e}")

    def _load_metadata(self):
        """Load metadata from disk if it exists"""
        metadata_path = os.path.join(GW_ROOT, "services", "images", "metadata.json")

        try:
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    data = json.load(f)
                    self.image_metadata = {int(k): v for k, v in data["image_metadata"].items()}

                    self.global_image_idx = data["global_image_idx"]
        except Exception as e:
            print(f"Error loading metadata: {e}")

    def _save_metadata(self):
        """Save metadata to disk"""
        metadata_path = os.path.join(GW_ROOT, "services", "images", "metadata.json")

        try:
            data = {
                "image_metadata": self.image_metadata,
                "global_image_idx": self.global_image_idx,
            }
            with open(metadata_path, 'w') as f:
                f.write(json.dumps(data, indent=4))

        except Exception as e:
            print(f"Error saving metadata: {e}")

    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.shutdown()
        signal.default_int_handler(signum, frame)

    def shutdown(self):
        """Clean shutdown procedure to save all data"""
        print("Shutting down AI service, saving data...")
        self._save_metadata()
        self.tag_retrieval._save_transform_and_contexts()

        print("AI service data saved successfully")

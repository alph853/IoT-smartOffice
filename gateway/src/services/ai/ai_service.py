import os
import json
import base64
import threading
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Callable
from PIL import Image
import io
import imagehash
from loguru import logger

from src.domain.repositories import HttpClientRepository, CacheClientRepository
from src.domain.events import EventBusInterface, TelemetryEvent
from .tag_retrieval import TagRetrieval
from .clip_retrieval import ClipRetrieval
from .inference_processor import InferenceProcessor


class AIMultimediaService:
    """AI service for multimedia processing and retrieval in smart office"""
    
    def __init__(self, 
                 event_bus: EventBusInterface,
                 http_client: HttpClientRepository,
                 cache_client: CacheClientRepository,
                 image_save_dir: str = "data/images",
                 batch_size: int = 16,
                 timeout_seconds: int = 30):
        
        self.event_bus = event_bus
        self.http_client = http_client
        self.cache_client = cache_client
        
        # Image storage setup
        self.image_save_dir = os.path.join(os.getcwd(), image_save_dir)
        self.global_image_idx = 0
        self.image_metadata = {}
        self.prev_image_hash = None
        os.makedirs(self.image_save_dir, exist_ok=True)
        
        # Processing setup
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.queued_images = []
        self.processing_lock = threading.Lock()
        self.processor_event = threading.Event()
        
        # Retrieval components
        self.tag_retrieval = TagRetrieval(data_dir=os.path.join(os.getcwd(), "data/ai"))
        self.clip_retrieval = ClipRetrieval(data_dir=os.path.join(os.getcwd(), "data/ai"))
        
        # Inference processor
        self.inference_processor = InferenceProcessor()
        
        # Load existing metadata
        self._load_metadata()
        
        # Background processing thread
        self._processing_thread = None
        self._stop_event = threading.Event()
        
    async def start(self):
        """Start the AI multimedia service"""
        # Subscribe to camera telemetry events
        await self.event_bus.subscribe(TelemetryEvent, self._handle_camera_telemetry)
        
        # Start background processing thread
        self._processing_thread = threading.Thread(target=self._processor_loop, daemon=True)
        self._processing_thread.start()
        
        logger.info("AI Multimedia service started")
        
    async def stop(self):
        """Stop the AI multimedia service"""
        await self.event_bus.unsubscribe(TelemetryEvent, self._handle_camera_telemetry)
        
        # Stop processing thread
        self._stop_event.set()
        self.processor_event.set()  # Wake up the processor
        
        if self._processing_thread:
            self._processing_thread.join(timeout=5)
            
        # Save metadata and contexts
        self._save_metadata()
        self.tag_retrieval.save_contexts()
        
        logger.info("AI Multimedia service stopped")
    
    async def _handle_camera_telemetry(self, event: TelemetryEvent):
        """Handle telemetry events from camera devices"""
        device = await self.cache_client.get_device_by_id(event.device_id)
        
        if not device or not self._is_camera_device(device):
            return
            
        # Check if telemetry contains image data
        image_data_b64 = event.data.get("image")
        if not image_data_b64:
            return
            
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_data_b64)
            
            # Process and save the image
            filepath = await self._save_captured_image(image_data, device.id)
            
            if filepath:
                logger.info(f"Captured image from device {device.name}: {filepath}")
                
        except Exception as e:
            logger.error(f"Error processing camera telemetry: {e}")
    
    def _is_camera_device(self, device) -> bool:
        """Check if device is a camera based on sensors"""
        if not device.sensors:
            return False
            
        for sensor in device.sensors:
            if sensor.type in ["camera", "image_sensor", "video"]:
                return True
        return False
    
    async def _save_captured_image(self, image_data: bytes, device_id: int) -> Optional[str]:
        """Save captured image and queue for processing"""
        try:
            # Check for duplicate images using perceptual hash
            image = Image.open(io.BytesIO(image_data))
            current_hash = imagehash.phash(image)
            
            if self.prev_image_hash is not None:
                distance = current_hash - self.prev_image_hash
                if distance < 5:  # Skip similar images
                    return None
                    
            self.prev_image_hash = current_hash
            
            # Generate filename with timestamp
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond // 1000:02d}"
            filename = f"device_{device_id}_{timestamp}.jpg"
            filepath = os.path.join(self.image_save_dir, filename)
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            # Update metadata
            self.image_metadata[self.global_image_idx] = {
                "filename": filename,
                "device_id": device_id,
                "timestamp": now.isoformat(),
                "filepath": filepath
            }
            self.global_image_idx += 1
            
            # Queue for processing
            with self.processing_lock:
                self.queued_images.append({
                    "filepath": filepath,
                    "metadata_idx": self.global_image_idx - 1,
                    "device_id": device_id
                })
            
            # Trigger processing if batch is full
            if len(self.queued_images) >= self.batch_size:
                self.processor_event.set()
                
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving captured image: {e}")
            return None
    
    def _processor_loop(self):
        """Background thread for processing image batches"""
        while not self._stop_event.is_set():
            # Wait for batch or timeout
            self.processor_event.wait(self.timeout_seconds)
            self.processor_event.clear()
            
            if self._stop_event.is_set():
                break
                
            # Get batch to process
            with self.processing_lock:
                if not self.queued_images:
                    continue
                    
                batch = self.queued_images[:self.batch_size]
                self.queued_images = self.queued_images[self.batch_size:]
            
            # Process batch
            asyncio.run(self._process_batch(batch))
    
    async def _process_batch(self, batch: List[Dict]):
        """Process a batch of images"""
        if not batch:
            return
            
        try:
            filepaths = [item["filepath"] for item in batch]
            
            # Run inference
            tag_results = self.inference_processor.process_batch(filepaths, contexts=["tag"])
            
            if tag_results and "tag" in tag_results:
                tag_outputs, tag_contexts = tag_results["tag"]
                
                # Update retrieval system
                self.tag_retrieval.add_contexts(tag_contexts)
                
                # Prepare data for backend
                for i, item in enumerate(batch):
                    if i < len(tag_outputs):
                        metadata = self.image_metadata[item["metadata_idx"]]
                        metadata["tags"] = tag_outputs[i]
                        metadata["tag_context"] = tag_contexts[i]
                        
                        # Send to backend
                        await self._send_to_backend(metadata, item["device_id"])
                
                # Save updated metadata
                self._save_metadata()
                
                logger.info(f"Processed batch of {len(batch)} images")
                
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
    
    async def _send_to_backend(self, metadata: Dict, device_id: int):
        """Send processed image data to backend for storage in pgvector"""
        try:
            # Prepare data for backend API
            data = {
                "device_id": device_id,
                "filename": metadata["filename"],
                "timestamp": metadata["timestamp"],
                "tags": metadata.get("tags", []),
                "tag_embedding": metadata.get("tag_context", ""),
                "office_id": (await self.cache_client.get_device_by_id(device_id)).office_id
            }
            
            # Call backend API to store in pgvector
            # Assuming there's an endpoint for multimedia data
            response = await self.http_client.post("/multimedia/images", data)
            
            if response:
                logger.debug(f"Sent image data to backend: {metadata['filename']}")
                
        except Exception as e:
            logger.error(f"Error sending data to backend: {e}")
    
    async def search_images(self, query: str, search_type: str = "hybrid", k: int = 10) -> Dict:
        """Search for images using natural language or tags"""
        try:
            scores = []
            filenames = []
            
            if search_type in ["nl", "hybrid"]:
                # Natural language search using CLIP
                nl_scores, nl_indices = self.clip_retrieval.search(query, k)
                if nl_indices:
                    nl_filenames = [self.image_metadata[idx]["filename"] for idx in nl_indices if idx in self.image_metadata]
                    scores.extend(nl_scores)
                    filenames.extend(nl_filenames)
            
            if search_type in ["tag", "hybrid"]:
                # Tag-based search
                tag_scores, tag_indices = self.tag_retrieval.search(query, k)
                if tag_indices:
                    tag_filenames = [self.image_metadata[idx]["filename"] for idx in tag_indices if idx in self.image_metadata]
                    scores.extend(tag_scores)
                    filenames.extend(tag_filenames)
            
            # Remove duplicates and sort by score
            unique_results = {}
            for score, filename in zip(scores, filenames):
                if filename not in unique_results or score > unique_results[filename]:
                    unique_results[filename] = score
            
            sorted_results = sorted(unique_results.items(), key=lambda x: x[1], reverse=True)[:k]
            
            return {
                "results": [
                    {
                        "filename": filename,
                        "score": score,
                        "metadata": next((m for m in self.image_metadata.values() if m["filename"] == filename), {})
                    }
                    for filename, score in sorted_results
                ]
            }
            
        except Exception as e:
            logger.error(f"Error searching images: {e}")
            return {"results": [], "error": str(e)}
    
    def _load_metadata(self):
        """Load metadata from disk"""
        metadata_path = os.path.join(self.image_save_dir, "metadata.json")
        
        try:
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    data = json.load(f)
                    self.image_metadata = {int(k): v for k, v in data.get("image_metadata", {}).items()}
                    self.global_image_idx = data.get("global_image_idx", 0)
                    logger.info(f"Loaded {len(self.image_metadata)} image metadata entries")
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
    
    def _save_metadata(self):
        """Save metadata to disk"""
        metadata_path = os.path.join(self.image_save_dir, "metadata.json")
        
        try:
            data = {
                "image_metadata": self.image_metadata,
                "global_image_idx": self.global_image_idx
            }
            
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            
            with open(metadata_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug("Saved image metadata")
            
        except Exception as e:
            logger.error(f"Error saving metadata: {e}") 
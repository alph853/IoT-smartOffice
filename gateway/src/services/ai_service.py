import base64
import os
import cv2
import numpy as np
import asyncio
from PIL import Image
import torch
import clip
from datetime import datetime
from src.domain.repositories import HttpClientRepository


class AIMultimediaService:
    def __init__(self, http_client: HttpClientRepository):
        self.http_client = http_client
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.poll_interval = 0.5
        self.diff_threshold = 15.0
        self.esp32_cam_url = "http://192.168.1.247/capture"

        # Load the CLIP model (ViT‐B/32) and its preprocessing pipeline
        self.clip_model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        self.clip_model.eval()

        self.prev_gray: np.ndarray | None = None

    async def start(self):
        while True:
            frame = await self.fetch_frame_async()
            if frame is None:
                print("[WARN] fetch_frame_async failed")
                await asyncio.sleep(self.poll_interval)
                continue

            curr_gray = self.frame_to_grayscale(frame)

            if self.prev_gray is None:
                self.prev_gray = curr_gray
                await asyncio.sleep(self.poll_interval)
                continue

            if self.scene_has_changed(self.prev_gray, curr_gray, self.diff_threshold):
                print("[INFO] scene has changed")
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb)

                image_embedding = self.run_clip_inference(pil_img)
                success, jpeg_buffer = cv2.imencode(".jpg", frame)
                if not success:
                    raise RuntimeError("Could not encode frame as JPEG")

                # 2) Base64‐encode the JPEG bytes:
                jpg_bytes = jpeg_buffer.tobytes()           # e.g. b'\xff\xd8\xff...'
                b64str = base64.b64encode(jpg_bytes).decode("utf-8")

                await self.http_client.post(
                    "/multimedia/images",
                    {
                        "image_embedding": image_embedding.tolist(),
                        "image_data": b64str,
                        "created_at": datetime.now().isoformat()
                    }
                )

                self.prev_gray = curr_gray.copy()
            else:
                await asyncio.sleep(self.poll_interval)

    async def fetch_frame_async(self) -> np.ndarray | None:
        try:
            response = await self.http_client.get(self.esp32_cam_url, expect_json=False)
            if response:
                img = cv2.imdecode(np.frombuffer(response, np.uint8), cv2.IMREAD_COLOR)
                return img
            else:
                return None
        except Exception as e:
            print(f"[WARN] fetch_frame_async failed: {e}")
            return None

    @staticmethod
    def frame_to_grayscale(frame: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def scene_has_changed(prev_gray: np.ndarray, curr_gray: np.ndarray, threshold: float) -> bool:
        """
        Compute mean absolute difference between two grayscale frames.
        Return True if the mean difference is above the threshold.
        """
        diff = cv2.absdiff(prev_gray, curr_gray)
        mean_diff = float(np.mean(diff))
        return mean_diff > threshold

    def run_clip_inference(self, pil_img: Image.Image) -> torch.Tensor:
        """
        Given a PIL.Image, preprocess it for CLIP, encode it with clip_model.encode_image(),
        normalize the embedding to unit length, and return the resulting tensor of shape [1, D].
        """
        image_input = self.preprocess(pil_img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            image_features = self.clip_model.encode_image(image_input)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        return image_features

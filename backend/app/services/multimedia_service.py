import os
import base64
from typing import List
from datetime import datetime
from loguru import logger
import clip
import torch

from app.domain.models import MultimediaData, MultimediaResponse
from app.domain.repositories import MultimediaRepository


class MultimediaService:
    """Simple service for multimedia operations with image storage"""
    def __init__(self, multimedia_repository: MultimediaRepository):
        self.multimedia_repository = multimedia_repository
        self.image_storage_path = "data/images"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        os.makedirs(self.image_storage_path, exist_ok=True)
        
        self.clip_model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        self.clip_model.eval()
    
    async def save_multimedia_data(self, multimedia_data: MultimediaData) -> MultimediaData:
        """Save multimedia data and store image locally"""
        try:
            timestamp = datetime.now()
            unique_filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
            image_path = os.path.join(self.image_storage_path, unique_filename)
            
            try:
                image_bytes = base64.b64decode(multimedia_data.image_data)
                with open(image_path, 'wb') as f:
                    f.write(image_bytes)
                logger.info(f"Saved image to: {image_path}")
            except Exception as e:
                logger.error(f"Error saving image: {e}")
                raise Exception(f"Invalid image data: {e}")
            
            multimedia_data.filename   = unique_filename
            multimedia_data.image_path = image_path
            
            result = await self.multimedia_repository.save_multimedia_data(multimedia_data)
            return result
            
        except Exception as e:
            logger.error(f"Error saving multimedia data: {e}")
            raise
    
    async def get_multimedia_list(self, query: str = "", k: int = 100) -> MultimediaResponse:
        """Get multimedia list with actual image data"""
        try:
            text_tokens = clip.tokenize(query).to(self.device)
            text_features = self.clip_model.encode_text(text_tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

            response = await self.multimedia_repository.similarity_search(text_features, k)

            return response
            
        except Exception as e:
            logger.error(f"Error getting multimedia list: {e}")
            return [] 
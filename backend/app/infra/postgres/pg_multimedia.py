import os
import json
import base64
import pickle
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger
import torch
import numpy as np
import faiss

from app.domain.models import MultimediaData, MultimediaResponse, Image
from app.domain.repositories import MultimediaRepository
from app.infra.postgres.db import PostgreSQLConnection


class PostgresMultimediaRepository(MultimediaRepository):
    """PostgreSQL-based multimedia repository using file storage"""
    
    def __init__(self, db: PostgreSQLConnection, storage_path: str = "data/multimedia"):
        self.db = db
        self.storage_path = storage_path
        self.metadata_file = os.path.join(storage_path, "metadata.json")
        self.index_file = os.path.join(storage_path, "faiss_index.bin")
        self.embedding_dim = 512
        
        os.makedirs(storage_path, exist_ok=True)
        
        self.index = self._load_or_create_index()
        
        # Load existing metadata
        self.metadata: Dict[int, Dict[str, Any]] = self._load_metadata()
        self.next_id = max(self.metadata.keys(), default=0) + 1
        
        logger.info(f"FAISS multimedia repository initialized with {len(self.metadata)} items")
    
    def _load_or_create_index(self) -> faiss.Index:
        """Load existing FAISS index or create a new one"""
        if os.path.exists(self.index_file):
            try:
                index = faiss.read_index(self.index_file)
                logger.info(f"Loaded existing FAISS index with {index.ntotal} vectors")
                return index
            except Exception as e:
                logger.warning(f"Could not load FAISS index: {e}, creating new one")
        
        # Create new index using Inner Product (for cosine similarity with normalized vectors)
        index = faiss.IndexFlatIP(self.embedding_dim)
        logger.info("Created new FAISS index")
        return index
    
    def _load_metadata(self) -> Dict[int, Dict[str, Any]]:
        """Load metadata from JSON file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to integers
                    return {int(k): v for k, v in data.items()}
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}, starting fresh")
        
        return {}
    
    def _save_metadata(self):
        """Save metadata to JSON file"""
        try:
            # Convert integer keys to strings for JSON serialization
            json_data = {str(k): v for k, v in self.metadata.items()}
            
            with open(self.metadata_file, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
            
            logger.debug("Saved metadata to file")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            raise
    
    def _save_index(self):
        """Save FAISS index to file"""
        try:
            faiss.write_index(self.index, self.index_file)
            logger.debug("Saved FAISS index to file")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            raise
    
    async def save_multimedia_data(self, multimedia: MultimediaData) -> MultimediaData:
        """Save multimedia data with FAISS indexing"""
        try:
            # Assign ID
            multimedia.id = self.next_id
            self.next_id += 1
            
            # Convert embedding to numpy array
            if isinstance(multimedia.image_embedding, torch.Tensor):
                embedding_array = multimedia.image_embedding.detach().cpu().numpy()
            elif isinstance(multimedia.image_embedding, list):
                embedding_array = np.array(multimedia.image_embedding, dtype=np.float32)
            else:
                embedding_array = multimedia.image_embedding
            
            # Ensure it's the right shape and normalized
            if embedding_array.ndim == 1:
                embedding_array = embedding_array.reshape(1, -1)
            
            # Normalize for cosine similarity
            embedding_array = embedding_array / np.linalg.norm(embedding_array, axis=1, keepdims=True)
            
            # Add to FAISS index
            self.index.add(embedding_array.astype(np.float32))
            
            # Store metadata
            self.metadata[multimedia.id] = {
                "id": multimedia.id,
                "filename": multimedia.filename,
                "image_path": multimedia.image_path,
                "created_at": multimedia.created_at.isoformat() if isinstance(multimedia.created_at, datetime) else multimedia.created_at,
                "embedding_index": len(self.metadata)  # Position in FAISS index
            }
            
            # Save to files
            self._save_metadata()
            self._save_index()
            
            logger.info(f"Saved multimedia data with ID {multimedia.id}: {multimedia.filename}")
            return multimedia
            
        except Exception as e:
            logger.error(f"Error saving multimedia data: {e}")
            raise
    
    async def similarity_search(self, query_embedding, limit: int = 10) -> MultimediaResponse:
        """Perform similarity search using FAISS"""
        try:
            if len(self.metadata) == 0:
                logger.info("No multimedia data available for search")
                return MultimediaResponse(images=[])
            
            # Convert query embedding to numpy array
            if isinstance(query_embedding, torch.Tensor):
                query_array = query_embedding.detach().cpu().numpy()
            elif isinstance(query_embedding, list):
                query_array = np.array(query_embedding, dtype=np.float32)
            else:
                query_array = query_embedding
            
            # Ensure correct shape and normalize
            if query_array.ndim == 1:
                query_array = query_array.reshape(1, -1)
            
            query_array = query_array / np.linalg.norm(query_array, axis=1, keepdims=True)
            
            # Perform FAISS search
            scores, indices = self.index.search(query_array.astype(np.float32), min(limit, self.index.ntotal))
            
            # Get results
            images = []
            metadata_list = list(self.metadata.values())
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for invalid indices
                    continue
                
                if idx < len(metadata_list):
                    meta = metadata_list[idx]
                    
                    # Load image data from file
                    image_data = ""
                    try:
                        if meta['image_path'] and os.path.exists(meta['image_path']):
                            with open(meta['image_path'], 'rb') as f:
                                image_bytes = f.read()
                                image_data = base64.b64encode(image_bytes).decode('utf-8')
                    except Exception as e:
                        logger.warning(f"Could not load image from {meta['image_path']}: {e}")
                    
                    # Parse datetime
                    created_at = meta['created_at']
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except:
                            created_at = datetime.now()
                    
                    images.append(Image(
                        filename=meta['filename'],
                        image_data=image_data,
                        created_at=created_at
                    ))
                    
                    logger.debug(f"Found similar image: {meta['filename']} (score: {score:.4f})")
            
            logger.info(f"Similarity search returned {len(images)} results")
            return MultimediaResponse(images=images)
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            return MultimediaResponse(images=[])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics"""
        return {
            "total_items": len(self.metadata),
            "faiss_index_size": self.index.ntotal,
            "embedding_dimension": self.embedding_dim,
            "storage_path": self.storage_path
        } 
from abc import ABC, abstractmethod
from typing import List
from ..models import MultimediaData
import torch


class MultimediaRepository(ABC):
    @abstractmethod
    async def save_multimedia_data(self, multimedia: MultimediaData) -> MultimediaData:
        """Save multimedia data to database"""
        pass

    @abstractmethod
    async def similarity_search(self, query: torch.Tensor, limit: int = 100) -> List[str]:
        """Get all multimedia data with optional text search"""
        pass 
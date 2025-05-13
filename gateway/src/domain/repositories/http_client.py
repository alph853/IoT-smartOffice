from abc import ABC, abstractmethod
from typing import List

from src.domain.models import Device


class HttpClientRepository(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def get_all_devices(self) -> List[Device]:
        pass

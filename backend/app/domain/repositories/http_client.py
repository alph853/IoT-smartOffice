from abc import ABC, abstractmethod
from typing import Dict, Any


class HttpClientRepository(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass


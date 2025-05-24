from abc import ABC, abstractmethod
from typing import Dict, Any


class HttpClientRepository(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def request(self,
                      url: str,
                      payload: dict | None = None,
                      method: str = "GET",
                      headers: dict | None = None):
        pass

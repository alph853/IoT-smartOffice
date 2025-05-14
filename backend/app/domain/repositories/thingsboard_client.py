from typing import Dict, Any
from abc import ABC, abstractmethod


class MqttCloudClientRepository(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass


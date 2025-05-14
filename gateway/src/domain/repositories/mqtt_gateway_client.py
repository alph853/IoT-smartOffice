from abc import ABC, abstractmethod

from src.domain.models import Device


class MqttGatewayClientRepository(ABC):
    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass
    # -------------------------------------------------------------
    # ------------------------- Publisher -------------------------
    # -------------------------------------------------------------

    @abstractmethod
    async def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False):
        pass

    @abstractmethod
    async def register_device(self, device: Device):
        pass

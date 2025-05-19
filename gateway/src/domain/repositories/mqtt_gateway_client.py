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
    async def register_device(self, device: Device):
        pass

    @abstractmethod
    async def connect_device(self, device: Device):
        pass

    @abstractmethod
    async def disconnect_device(self, device: Device):
        pass

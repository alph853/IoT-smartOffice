from abc import ABC, abstractmethod
from typing import List

from src.domain.models import Device, DeviceCreate


class HttpClientRepository(ABC):
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
    # ------------------------- Device ----------------------------
    # -------------------------------------------------------------

    @abstractmethod
    async def get_all_devices(self) -> List[Device]:
        pass

    @abstractmethod
    async def connect_device(self, device: Device) -> Device | None:
        pass

    @abstractmethod
    async def create_device(self, device: DeviceCreate) -> Device | None:
        pass

    @abstractmethod
    async def update_device(self, device: Device) -> Device | None:
        pass
    
    @abstractmethod
    async def delete_device(self, device_id: str) -> bool:
        pass

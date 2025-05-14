from abc import ABC, abstractmethod
from typing import List

from src.domain.models import Device


class CacheClientRepository(ABC):
    # ----------------------------------------------------------
    # ------------------------- Device -------------------------
    # ----------------------------------------------------------

    @abstractmethod
    async def get_all_devices(self) -> List[Device]:
        pass

    @abstractmethod
    async def get_device_by_mac_addr(self, mac_addr: str) -> Device | None:
        pass
    
    @abstractmethod
    async def add_device(self, device: Device) -> bool:
        pass
    
    @abstractmethod
    async def remove_device(self, device_id: str) -> bool:
        pass
    
    @abstractmethod
    async def update_device(self, device: Device) -> bool:
        pass

    # ----------------------------------------------------------
    # ------------------------ Control -------------------------
    # ----------------------------------------------------------
    @abstractmethod
    async def get_control_device(self, device_id: str) -> Device | None:
        pass
    
    @abstractmethod
    async def update_control_device(self, device_id: str, info: dict) -> bool:
        pass
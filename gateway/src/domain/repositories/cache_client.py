from abc import ABC, abstractmethod
from typing import List

from src.domain.models import Device, DeviceStatus, DeviceMode


class CacheClientRepository(ABC):
    # ----------------------------------------------------------
    # ------------------------- Device -------------------------
    # ----------------------------------------------------------

    @abstractmethod
    async def get_all_devices(self) -> List[Device]:
        pass

    @abstractmethod
    async def get_device_by_id(self, device_id: str) -> Device:
        pass

    @abstractmethod
    async def add_device(self, device: Device) -> Device:
        pass

    @abstractmethod
    async def delete_device(self, device_id: str) -> bool:
        pass

    @abstractmethod
    async def update_device(self, device_id: str, info: dict) -> bool:
        pass
    
    @abstractmethod
    async def get_status(self, device_id: str) -> DeviceStatus:
        pass

    @abstractmethod
    async def get_device_by_mac(self, mac_address: str) -> Device | None:
        pass

    @abstractmethod
    async def get_mode(self, device_id: str) -> DeviceMode:
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

    @abstractmethod
    async def get_device_id_by_actuator_id(self, actuator_id: int) -> int | None:
        pass


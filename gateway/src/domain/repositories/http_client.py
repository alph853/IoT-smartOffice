from abc import ABC, abstractmethod
from typing import List, Dict, Any

from src.domain.models import Device, DeviceCreate, DeviceStatus


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
    # ------------------------- Generic HTTP ----------------------
    # -------------------------------------------------------------

    @abstractmethod
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any] | None:
        """Generic POST method for sending data to any endpoint"""
        pass

    @abstractmethod
    async def get(self, endpoint: str, use_server_url: bool = False) -> Dict[str, Any] | None:
        """Generic GET method for sending data to any endpoint"""
        pass
        
    # -------------------------------------------------------------
    # ------------------------- Device ----------------------------
    # -------------------------------------------------------------

    @abstractmethod
    async def get_all_devices(self, return_components: bool = False) -> List[Device]:
        pass

    @abstractmethod
    async def connect_device(self, device: Device) -> Device | None:
        pass

    @abstractmethod
    async def create_device(self, device: DeviceCreate) -> Device | None:
        pass

    @abstractmethod
    async def update_device(self, device_id: int, data: Dict[str, Any]) -> Device | None:
        pass
    
    @abstractmethod
    async def delete_device(self, device_id: str) -> bool:
        pass
    
    @abstractmethod
    async def set_device_status(self, device_id: str, status: DeviceStatus) -> bool:
        pass
    

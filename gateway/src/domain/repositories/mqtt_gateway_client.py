from abc import ABC, abstractmethod
from typing import Callable, Dict, Any

from src.domain.models import Device
from src.domain.events import SetLightingEvent, SetFanStateEvent, RPCTestEvent


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
    # ------------------------- Subscriber ------------------------
    # -------------------------------------------------------------
    
    @abstractmethod
    async def get_topics(self) -> Dict[str, Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str, callback: Callable):
        pass
    
    @abstractmethod
    async def unsubscribe(self, topic: str):
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

    @abstractmethod
    async def set_lighting(self, event: SetLightingEvent) -> bool:
        pass

    @abstractmethod
    async def set_fan_state(self, event: SetFanStateEvent) -> bool:
        pass

    @abstractmethod
    async def send_test_command(self, event: RPCTestEvent) -> bool:
        pass

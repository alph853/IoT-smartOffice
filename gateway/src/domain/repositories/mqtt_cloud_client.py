from abc import ABC, abstractmethod
from typing import Callable

from src.domain.models import DeviceRegistration, Device


class MqttCloudClientRepository(ABC):
    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass
    
    # -------------------------------------------------------------
    # ------------------------- Publish -------------------------
    # -------------------------------------------------------------

    @abstractmethod
    def connect_device(self, device: Device):
        pass
    
    @abstractmethod
    def disconnect_device(self, device: Device):
        pass
    
    @abstractmethod
    def send_telemetry(self, device: Device, telemetry: dict, qos: int = 1):
        pass

    @abstractmethod
    def send_attributes(self, device: Device, attributes: dict, qos: int = 1):
        pass

    @abstractmethod
    def send_rpc_reply(self, device: Device, method: str, params: dict, qos: int = 1):
        pass
    
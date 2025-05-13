from abc import ABC, abstractmethod
from typing import Callable


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

    @abstractmethod
    def messages(self):
        pass
    
    # -------------------------------------------------------------
    # ------------------------- Publish -------------------------
    # -------------------------------------------------------------

    @abstractmethod
    def publish_telemetry(self, topic: str, payload: str, qos: int, retain: bool):
        pass

    @abstractmethod
    def publish_rpc_response(self, topic: str, payload: str, qos: int, retain: bool):
        pass
    
    @abstractmethod
    def publish_rpc_request(self, topic: str, payload: str, qos: int, retain: bool):
        pass
    
    
    
    
from abc import ABC, abstractmethod


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

    @abstractmethod
    def messages(self):
        pass

    # -------------------------------------------------------------
    # ------------------------- Publisher -------------------------
    # -------------------------------------------------------------

    @abstractmethod
    async def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False):
        pass


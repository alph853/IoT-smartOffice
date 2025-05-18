from abc import ABC, abstractmethod

from app.domain.models import ModeSet, LightingSet, DisconnectDevice, RPCResponse


class MqttCloudClientRepository(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    # ------------------------------------------------------------
    # ----------------------------- RPC --------------------------
    # ------------------------------------------------------------

    @abstractmethod
    async def set_mode(self, request: ModeSet) -> RPCResponse:
        pass

    @abstractmethod
    async def set_lighting(self, request: LightingSet) -> RPCResponse:
        pass

    @abstractmethod
    async def test_rpc(self) -> RPCResponse:
        pass

    @abstractmethod
    async def disconnect_device(self, request: DisconnectDevice) -> RPCResponse:
        pass
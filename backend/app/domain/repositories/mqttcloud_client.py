from abc import ABC, abstractmethod
from typing import Dict, Any
from app.domain.models import DeviceUpdate, RPCResponse, ActuatorUpdate


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
    async def send_rpc_command(self, request: Dict[str, Any]) -> RPCResponse:
        pass

    @abstractmethod
    async def delete_device(self, device_id: int) -> RPCResponse:
        pass

    @abstractmethod
    async def update_device(self, device_id: int, device_update: DeviceUpdate) -> RPCResponse:
        pass

    @abstractmethod
    async def update_actuator(self, actuator_id: int, actuator_update: ActuatorUpdate) -> RPCResponse:
        pass

    @abstractmethod
    async def get_client_id(self, device_name: str) -> str:
        pass

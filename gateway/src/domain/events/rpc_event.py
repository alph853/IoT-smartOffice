from pydantic import BaseModel
from typing import Tuple

from src.domain.models import DeviceMode, DeviceStatus


class RPCRequest(BaseModel):
    request_id: str


class DeleteDeviceEvent(RPCRequest):
    device_id: int


class UpdateDeviceEvent(RPCRequest):
    device_id: int
    device_update: dict


class GatewayDeviceDeletedEvent(RPCRequest):
    pass


class UpdateActuatorEvent(RPCRequest):
    actuator_id: int
    actuator_update: dict


SingleColorType = Tuple[int, int, int]
Led4ColorType = Tuple[SingleColorType, SingleColorType, SingleColorType, SingleColorType]

class SetLightingEvent(RPCRequest):
    actuator_id: int
    color: Led4ColorType


class SetFanStateEvent(RPCRequest):
    actuator_id: int
    state: bool


class RPCTestEvent(RPCRequest):
    device_id: int
    message: str


class InvalidRPCEvent(RPCRequest):
    params: dict
    method: str


class UnknownEvent(RPCRequest):
    device_id: int
    method: str


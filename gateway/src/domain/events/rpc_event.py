from pydantic import BaseModel
from typing import Tuple

from src.domain.models import DeviceMode, DeviceStatus


class RPCRequest(BaseModel):
    request_id: int | None = None


class DeleteDeviceEvent(RPCRequest):
    device_id: int


class UpdateDeviceEvent(RPCRequest):
    device_id: int
    device_update: dict


class GatewayDeviceDeletedEvent(RPCRequest):
    pass


class UpdateActuatorEvent(RPCRequest):
    device_id: int
    actuator_update: dict


class SetModeEvent(RPCRequest):
    device_id: int
    mode: DeviceMode


class SetLightingEvent(RPCRequest):
    actuator_id: int
    color: Tuple[int, int, int]


class SetFanStateEvent(RPCRequest):
    actuator_id: int
    fan_state: bool


class RPCTestEvent(RPCRequest):
    device_id: int
    message: str


class InvalidRPCEvent(RPCRequest):
    params: dict
    method: str


class UnknownEvent(RPCRequest):
    device_id: int
    method: str


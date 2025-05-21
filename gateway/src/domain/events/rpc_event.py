from pydantic import BaseModel
from typing import Tuple

from src.domain.models import DeviceMode, DeviceStatus


class RPCRequest(BaseModel):
    request_id: str | None = None


class DeleteDeviceEvent(RPCRequest):
    device_id: str


class UpdateDeviceEvent(RPCRequest):
    device_id: str
    device_update: dict


class GatewayDeviceDeletedEvent(RPCRequest):
    pass


class UpdateActuatorEvent(RPCRequest):
    device_id: str
    actuator_update: dict


class SetModeEvent(RPCRequest):
    device_id: str
    mode: DeviceMode


class SetLightingEvent(RPCRequest):
    actuator_id: str
    color: Tuple[int, int, int]


class SetFanStateEvent(RPCRequest):
    actuator_id: str
    fan_state: bool


class RPCTestEvent(RPCRequest):
    device_id: str
    message: str


class InvalidRPCEvent(RPCRequest):
    params: dict
    method: str


class UnknownEvent(RPCRequest):
    device_id: str
    method: str


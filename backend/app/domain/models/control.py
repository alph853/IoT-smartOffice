from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from app.domain.models import DeviceMode, Device


class RPCRequest(BaseModel):
    method: str


class RPCResponse(BaseModel):
    status: str
    data: dict | None = None


class SupportedColor(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    PURPLE = "purple"
    ORANGE = "orange"


class LightingSetParams(BaseModel):
    brightness: int
    color: SupportedColor
    actuator_id: int | None = None


class LightingSet(RPCRequest):
    params: LightingSetParams


class ModeSetParams(BaseModel):
    mode: DeviceMode
    actuator_id: int | None = None


class ModeSet(RPCRequest):
    params: ModeSetParams


class DisconnectDeviceParams(BaseModel):
    device: Device


class DisconnectDevice(RPCRequest):
    params: DisconnectDeviceParams

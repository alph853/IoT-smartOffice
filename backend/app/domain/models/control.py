from pydantic import BaseModel
from enum import Enum
from typing import Tuple

from app.domain.models import Notification


COLOR_MAP = {
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "orange": (255, 165, 0),
    "white": (255, 255, 255),
    "pink": (255, 192, 203),
    "off": (0, 0, 0),
}


class BroadcastMessage(BaseModel):
    method: str
    params: Notification | None = None


class SupportedColor(str, Enum):
    YELLOW = "yellow"
    PURPLE = "purple"
    ORANGE = "orange"
    WHITE = "white"
    PINK = "pink"
    OFF = "off"

# Base RPC Models
class RPCRequest(BaseModel):
    method: str


class RPCResponse(BaseModel):
    status: str
    data: dict | None = None


# Parameter Models
ColorType = SupportedColor | Tuple[int, int, int]
ColorTuple = Tuple[ColorType, ColorType, ColorType, ColorType]

class LightingSetParams(BaseModel):
    brightness: int = 100
    color: ColorTuple
    actuator_id: int | None = None


class FanStateSetParams(BaseModel):
    state: bool
    actuator_id: int | None = None


# RPC Request Models
class LightingSet(RPCRequest):
    params: LightingSetParams


class FanStateSet(RPCRequest):
    params: FanStateSetParams

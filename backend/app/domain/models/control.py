from pydantic import BaseModel
from enum import Enum
from typing import Tuple


COLOR_MAP = {
    "yellow": [255, 255, 0],
    "purple": [128, 0, 128],
    "orange": [255, 165, 0],
    "white": [255, 255, 255],
    "pink": [255, 192, 203]
}


class SupportedColor(str, Enum):
    YELLOW = "yellow"
    PURPLE = "purple"
    ORANGE = "orange"
    WHITE = "white"
    PINK = "pink"

# Base RPC Models
class RPCRequest(BaseModel):
    method: str


class RPCResponse(BaseModel):
    status: str
    data: dict | None = None

# Parameter Models
class LightingSetParams(BaseModel):
    brightness: int = 100
    color: SupportedColor | Tuple[int, int, int]
    actuator_id: int | None = None


class FanStateSetParams(BaseModel):
    state: bool
    actuator_id: int | None = None


# RPC Request Models
class LightingSet(RPCRequest):
    params: LightingSetParams


class FanStateSet(RPCRequest):
    params: FanStateSetParams

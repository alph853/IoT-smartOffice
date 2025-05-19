from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from app.domain.models import DeviceMode, DeviceUpdate

# Enums


class SupportedColor(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    PURPLE = "purple"
    ORANGE = "orange"

# Base RPC Models
class RPCRequest(BaseModel):
    method: str

class RPCResponse(BaseModel):
    status: str
    data: dict | None = None

# Parameter Models
class LightingSetParams(BaseModel):
    brightness: int
    color: SupportedColor
    actuator_id: int | None = None

class FanStateSetParams(BaseModel):
    state: bool
    actuator_id: int | None = None


# RPC Request Models
class LightingSet(RPCRequest):
    params: LightingSetParams

class FanStateSet(RPCRequest):
    params: FanStateSetParams

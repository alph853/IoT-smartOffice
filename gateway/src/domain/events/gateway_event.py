from pydantic import BaseModel
from datetime import datetime

from src.domain.models import DeviceRegistration


class RegisterRequestEvent(BaseModel):
    device: DeviceRegistration


class InvalidMessageEvent(BaseModel):
    topic: str
    payload: str
    error: str


class TelemetryEvent(BaseModel):
    device_id: str
    timestamp: int = datetime.now().timestamp()
    data: dict


class ControlResponseEvent(BaseModel):
    status: str
    data: dict


class TestEvent(BaseModel):
    payload: str

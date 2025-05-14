from pydantic import BaseModel

from src.domain.models import DeviceRegistration


class RegisterRequestEvent(BaseModel):
    device: DeviceRegistration


class InvalidMessageEvent(BaseModel):
    topic: str
    payload: str
    error: str


class TestEvent(BaseModel):
    payload: str

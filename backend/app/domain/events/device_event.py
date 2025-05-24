from app.domain.models import Device
from pydantic import BaseModel


class DeviceConnectedEvent(BaseModel):
    device: Device


class DeviceDisconnectedEvent(BaseModel):
    device: Device

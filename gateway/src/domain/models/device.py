from pydantic import BaseModel
from typing import List
from enum import Enum


class Sensor(BaseModel):
    name: str
    description: str | None = None
    unit: str | None = None
    type: str | None = None


class Actuator(BaseModel):
    name: str
    description: str | None = None
    type: str | None = None


class DeviceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DISABLED = "disabled"


class DeviceMode(Enum):
    AUTO = "auto"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    OFFLINE = "offline"
    

class Device(BaseModel):
    id: int
    name: str
    mode: DeviceMode
    fw_version: str
    status: DeviceStatus
    access_token: str | None = None
    mac_addr: str

    class Config:
        use_enum_values = True

class DeviceRegistration(BaseModel):
    name: str
    mac_addr: str
    fw_version: str
    model: str
    description: str | None = None
    office_id: int
    sensors: List[Sensor]
    actuators: List[Actuator]


class DeviceCreate(DeviceRegistration):
    gateway_id: int

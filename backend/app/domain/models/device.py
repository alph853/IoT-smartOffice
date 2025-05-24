from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DeviceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DISABLED = "disabled"

    class Config:
        use_enum_values = True


class DeviceMode(Enum):
    AUTO = "auto"
    MANUAL = "manual"
    SCHEDULED = "scheduled"

    class Config:
        use_enum_values = True


class Sensor(BaseModel):
    id: int | None = None
    name: str
    type: str | None = None
    unit: str | None = None
    device_id: int | None = None


class SensorUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    unit: str | None = None


class Actuator(BaseModel):
    id: int | None = None
    name: str
    type: str | None = None
    device_id: int | None = None
    mode: DeviceMode = DeviceMode.MANUAL

    class Config:
        use_enum_values = True


class ActuatorUpdate(BaseModel):
    mode: DeviceMode | None = None
    name: str | None = None
    type: str | None = None

    class Config:
        use_enum_values = True

class SensorReadingCreate(BaseModel):
    data: Dict[str, Any]
    cap_id: int
    ts: datetime


class SensorReading(SensorReadingCreate):
    id: int


class DeviceRegistration(BaseModel):
    mac_addr: str
    fw_version: str
    model: str
    name: str
    gateway_id: int
    office_id: int
    description: str | None = None
    sensors: List[Sensor]
    actuators: List[Actuator]


class Device(BaseModel):
    id: int | None = None
    name: str
    registered_at: datetime = datetime.now()
    mac_addr: str
    description: str | None = None
    fw_version: str
    last_seen_at: datetime = datetime.now()
    model: str | None = None
    office_id: int
    gateway_id: int
    status: DeviceStatus = DeviceStatus.ONLINE
    access_token: str | None = None

    class Config:
        use_enum_values = True


class DeviceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    fw_version: str | None = None
    model: str | None = None
    office_id: int | None = None
    gateway_id: int | None = None
    status: DeviceStatus | None = None
    access_token: str | None = None
    last_seen_at: datetime | None = None

    class Config:
        use_enum_values = True


class Gateway(BaseModel):
    id: int | None = None
    name: str
    status: str
    office_id: int


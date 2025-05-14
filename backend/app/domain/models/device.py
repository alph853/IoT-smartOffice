from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Sensor(BaseModel):
    id: int | None = None
    name: str
    type: str
    unit: str
    device_id: int | None = None


class Actuator(BaseModel):
    id: int | None = None
    name: str
    type: str
    device_id: int | None = None


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


class Device(BaseModel):
    id: int | None = None
    name: str
    mode: DeviceMode
    registered_at: datetime | None = None
    mac_addr: str
    description: str | None = None
    fw_version: str
    last_seen_at: datetime | None = None
    model: str
    office_id: int
    gateway_id: int
    status: DeviceStatus
    access_token: str | None = None



class Gateway(BaseModel):
    id: int | None = None
    name: str
    status: str
    office_id: int


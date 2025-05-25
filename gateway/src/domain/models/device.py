from pydantic import BaseModel
from typing import List
from enum import Enum



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


class Sensor(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None
    unit: str | None = None
    status: DeviceStatus | None = None
    type: str | None = None
    device_id: int | None = None

    class Config:
        use_enum_values = True


class Actuator(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None
    mode: DeviceMode | None = None
    status: DeviceStatus | None = None
    type: str | None = None
    device_id: int | None = None
    setting: dict | None = None

    class Config:
        use_enum_values = True


class Device(BaseModel):
    id: int | None = None
    thingsboard_name: str
    fw_version: str
    status: DeviceStatus
    access_token: str | None = None
    mac_addr: str
    office_id: int
    sensors: List[Sensor] | None = None
    actuators: List[Actuator] | None = None

    class Config:
        use_enum_values = True


class DeviceRegistration(BaseModel):
    name: str
    mac_addr: str
    fw_version: str
    model: str | None = None
    description: str | None = None
    office_id: int
    gateway_id: int | None = None

    sensors: List[Sensor]
    actuators: List[Actuator]


class DeviceCreate(DeviceRegistration):
    gateway_id: int

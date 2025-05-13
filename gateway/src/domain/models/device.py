from pydantic import BaseModel
from typing import List


class Sensor(BaseModel):
    name: str
    description: str
    unit: str
    type: str


class Actuator(BaseModel):
    name: str
    description: str
    type: str


class Device(BaseModel):
    id: str
    name: str
    fw_version: str
    mac_addr: str
    mode: str
    sensors: List[Sensor]
    actuators: List[Actuator]
from pydantic import BaseModel
from typing import List
from enum import Enum


class Capability(Enum):
    temp: str = "temp"
    humidity: str = "humidity"
    light: str = "light"
    motion: str = "motion"
    sound: str = "sound"
    air_quality: str = "air_quality"
    

class RegisterMessage(BaseModel):
    fw_version: str
    name: str
    mac_addr: str
    capabilities: List[Capability]
    
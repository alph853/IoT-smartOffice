from pydantic import BaseModel
from typing import List, Optional
from .device import Device


class Office(BaseModel):
    id: int | None = None
    room: str | None = None
    building: str | None = None
    description: str | None = None
    name: str
    devices: Optional[List[Device]] = None


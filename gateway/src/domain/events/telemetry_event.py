from pydantic import BaseModel
from datetime import datetime


class TelemetryEvent(BaseModel):
    device_id: str
    timestamp: int = datetime.now().timestamp()
    data: dict

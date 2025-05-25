from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class NotificationType(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"


class Notification(BaseModel):
    id: int | None = None
    message: str
    read_status: bool = False
    type: NotificationType
    title: str
    device_id: int | None = None
    ts: datetime = datetime.now()

    class Config:
        use_enum_values = True

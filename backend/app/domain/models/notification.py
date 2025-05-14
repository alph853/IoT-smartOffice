from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime


class Notification(BaseModel):
    id: str
    type: str
    message: str
    severity: str
    timestamp: datetime
    read: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


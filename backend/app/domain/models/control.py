from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class ControlCommand(BaseModel):
    id: str
    device_id: str
    command_type: str
    parameters: Dict[str, Any]
    status: str
    timestamp: datetime
    executed_at: Optional[datetime] = None

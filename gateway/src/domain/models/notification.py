from dataclasses import dataclass
from datetime import datetime
    

@dataclass
class Notification:
    id: str
    title: str
    message: str
    created_at: datetime
    updated_at: datetime
    is_read: bool
    is_deleted: bool

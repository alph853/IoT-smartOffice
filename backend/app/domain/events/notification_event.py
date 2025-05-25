from pydantic import BaseModel
from datetime import datetime
from app.domain.models import Notification


class NotificationEvent(BaseModel):
    notification: Notification

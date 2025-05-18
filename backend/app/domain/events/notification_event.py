from pydantic import BaseModel
from app.domain.models import Notification


class NotificationEvent(BaseModel):
    notification: Notification

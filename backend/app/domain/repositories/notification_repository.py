from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import Notification


class NotificationRepository(ABC):
    @abstractmethod
    async def save_notification(self, notification: Notification) -> None:
        pass

    @abstractmethod
    async def get_notification(self, notification_id: str) -> Optional[Notification]:
        pass

    @abstractmethod
    async def get_unread_notifications(self) -> List[Notification]:
        pass

    @abstractmethod
    async def mark_as_read(self, notification_id: str) -> None:
        pass

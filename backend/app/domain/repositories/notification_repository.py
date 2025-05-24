from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import Notification


class NotificationRepository(ABC):
    @abstractmethod
    async def get_all_notifications(self) -> List[Notification]:
        pass

    @abstractmethod
    async def get_unread_notifications(self) -> List[Notification]:
        pass

    @abstractmethod
    async def get_notification_by_id(self, notification_id: str) -> Notification | None:
        pass

    @abstractmethod
    async def create_notification(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    async def mark_as_read(self, notification_id: str) -> bool:
        pass

    @abstractmethod
    async def mark_all_as_read(self) -> bool:
        pass

    @abstractmethod
    async def delete_all_notifications(self) -> bool:
        pass

    @abstractmethod
    async def delete_notification(self, notification_id: str) -> bool:
        pass


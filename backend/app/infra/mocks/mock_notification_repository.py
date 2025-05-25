from typing import List, Optional
from loguru import logger

from app.domain.models import Notification
from app.domain.repositories import NotificationRepository


class MockNotificationRepository(NotificationRepository):
    def __init__(self):
        self.notifications: List[Notification] = []

    async def get_all_notifications(self) -> List[Notification]:
        logger.info("Mock: Getting all notifications")
        return self.notifications

    async def get_unread_notifications(self) -> List[Notification]:
        logger.info("Mock: Getting unread notifications")
        return [n for n in self.notifications if not n.read_status]

    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        logger.info(f"Mock: Getting notification by ID {notification_id}")
        return next((n for n in self.notifications if n.id == notification_id), None)

    async def create_notification(self, notification: Notification) -> Notification:
        logger.info(f"Mock: Creating notification {notification}")
        self.notifications.append(notification)
        return notification

    async def mark_as_read(self, notification_id: str) -> bool:
        logger.info(f"Mock: Marking notification {notification_id} as read")
        for n in self.notifications:
            if n.id == notification_id:
                n.read_status = True
                return True
        return False

    async def mark_all_as_read(self) -> bool:
        logger.info("Mock: Marking all notifications as read")
        for n in self.notifications:
            n.read_status = True
        return True

    async def delete_all_notifications(self) -> bool:
        logger.info("Mock: Deleting all notifications")
        self.notifications.clear()
        return True

    async def delete_notification(self, notification_id: str) -> bool:
        logger.info(f"Mock: Deleting notification {notification_id}")
        initial_length = len(self.notifications)
        self.notifications = [n for n in self.notifications if n.id != notification_id]
        return len(self.notifications) < initial_length

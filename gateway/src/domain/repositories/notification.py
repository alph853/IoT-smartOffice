from abc import ABC, abstractmethod
from src.domain.models import Notification


class NotificationRepository(ABC):
    @abstractmethod
    def register(self, message: str):
        pass
    
    @abstractmethod
    async def send_notification(self, notification: Notification):
        pass

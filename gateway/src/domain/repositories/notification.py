
from abc import ABC, abstractmethod


class NotificationRepository(ABC):
    @abstractmethod
    def register(self, message: str):
        pass

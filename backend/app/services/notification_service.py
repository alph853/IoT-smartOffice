from app.domain.events import EventBusInterface


class NotificationService:
    def __init__(self, event_bus: EventBusInterface):
        self.event_bus = event_bus


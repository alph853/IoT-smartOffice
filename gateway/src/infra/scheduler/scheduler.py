from apscheduler.schedulers.background import BackgroundScheduler

from src.domain.events import EventBusInterface


class APScheduler:
    def __init__(self, event_bus: EventBusInterface):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.event_bus.publish, 'interval', seconds=1)
        self.scheduler.start()
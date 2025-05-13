
from loguru import logger

from src.domain.repositories import MqttCloudClientRepository
from src.domain.events import EventBusInterface, TelemetryEvent


class TelemetryService:
    def __init__(self, cloud_client: MqttCloudClientRepository, event_bus: EventBusInterface):
        self.cloud_client = cloud_client
        self.event_bus = event_bus

    async def subscribe_events(self):
        await self.event_bus.subscribe(TelemetryEvent, self.handle_telemetry)

    async def handle_telemetry(self, event: TelemetryEvent):
        logger.info(f"Received telemetry event: {event}")

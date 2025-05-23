
from loguru import logger

from src.domain.repositories import MqttCloudClientRepository, CacheClientRepository
from src.domain.events import EventBusInterface, TelemetryEvent
from src.domain.models import DeviceMode, DeviceStatus


class TelemetryService:
    def __init__(self, event_bus: EventBusInterface,
                 cache_client: CacheClientRepository,
                 cloud_client: MqttCloudClientRepository,
                 ):
        self.cache_client = cache_client
        self.cloud_client = cloud_client
        self.event_bus    = event_bus

    async def start(self):
        await self.event_bus.subscribe(TelemetryEvent, self._handle_telemetry)
        logger.info("Telemetry service started")

    async def stop(self):
        await self.event_bus.unsubscribe(TelemetryEvent, self._handle_telemetry)
        logger.info("Telemetry service stopped")

    async def _handle_telemetry(self, event: TelemetryEvent):
        device = await self.cache_client.get_device_by_id(event.device_id)
        if device:
            logger.info(f"Sending telemetry to {device.name} with {event.data}")
            try:
                status = await self.cache_client.get_status(device.id)
                # mode   = await self.cache_client.get_mode(device.id)
                if status == DeviceStatus.ONLINE:
                    self.cloud_client.send_telemetry(device.name, event.data)
            except Exception as e:
                logger.error(f"Error sending telemetry to {device.name}: {e}")
        else:
            logger.error(f"Device not found: {event.device_id}")

from loguru import logger
from typing import List

from src.domain.repositories import MqttCloudClientRepository, CacheClientRepository, HttpClientRepository, NotificationRepository
from src.domain.events import EventBusInterface, TelemetryEvent, SetLightingEvent, SetFanStateEvent
from src.domain.models import DeviceMode, DeviceStatus, Actuator, Notification


LUMINOUSITY_MIN = 0
LUMINOUSITY_MAX = 100
TEMPERATURE_MIN = 0
TEMPERATURE_MAX = 100


class TelemetryService:
    def __init__(self, event_bus: EventBusInterface,
                 cache_client: CacheClientRepository,
                 cloud_client: MqttCloudClientRepository,
                 http_client: HttpClientRepository = None,
                 notification_repo: NotificationRepository = None,
                 ):
        self.cache_client = cache_client
        self.cloud_client = cloud_client
        self.event_bus    = event_bus
        self.http_client = http_client
        self.notification_repo = notification_repo

    async def start(self):
        await self.event_bus.subscribe(TelemetryEvent, self._handle_telemetry)
        logger.info("Telemetry service started")

    async def stop(self):
        await self.event_bus.unsubscribe(TelemetryEvent, self._handle_telemetry)
        logger.info("Telemetry service stopped")

    async def _handle_telemetry(self, event: TelemetryEvent):
        device = await self.cache_client.get_device_by_id(event.device_id)
        if device:
            logger.info(f"Receive telemetry from {device.name} with {event.data}")
            try:
                # Check for error data
                if await self._check_error_data(device, event.data):
                    return
                
                if device.status == DeviceStatus.ONLINE.value:
                    self.cloud_client.send_telemetry(device.name, event.data)
                await self._handle_auto_actuator(device.actuators, event.data)
            except Exception as e:
                logger.error(f"Error sending telemetry to {device.name}: {e}")
        else:
            logger.error(f"Device not found: {event.device_id}")

    async def _check_error_data(self, device, data: dict) -> bool:
        """Check if telemetry data contains error values and handle accordingly"""
        has_error = False
        error_fields = []
        
        # Check each field for error value "E"
        for field, value in data.items():
            if value == "E":
                has_error = True
                error_fields.append(field)
        
        if has_error:
            logger.warning(f"Device {device.name} reported error data in fields: {error_fields}")
            
            # Update device status to ERROR
            device.status = DeviceStatus.ERROR
            await self.cache_client.set_device(device)
            
            # Update device status in backend if http_client is available
            if self.http_client:
                try:
                    await self.http_client.update_device(device.id, {"status": DeviceStatus.ERROR.value})
                except Exception as e:
                    logger.error(f"Failed to update device status in backend: {e}")
            
            # Send notification if notification repository is available
            if self.notification_repo:
                notification = Notification(
                    title=f"Device Error: {device.name}",
                    message=f"Device {device.name} reported error data in fields: {', '.join(error_fields)}",
                    type="error",
                    device_id=device.id
                )
                await self.notification_repo.send_notification(notification)
            
            # Still send the telemetry data to cloud for logging purposes
            if device.status == DeviceStatus.ERROR.value:
                self.cloud_client.send_telemetry(device.name, data)
            
        return has_error

    async def _handle_auto_actuator(self, actuators: List[Actuator], data: dict):
        luminousity = data.get("luminousity", "E")
        temperature = data.get("temperature", "E")

        if luminousity == "E" or temperature == "E":
            return

        luminousity = float(luminousity)
        temperature = float(temperature)
        lighting_color = (luminousity - LUMINOUSITY_MIN / (LUMINOUSITY_MAX - LUMINOUSITY_MIN))*255
        fan_state = (temperature - TEMPERATURE_MIN / (TEMPERATURE_MAX - TEMPERATURE_MIN)) > 0.2

        for actuator in actuators:
            if actuator.type == "led4RGB":
                await self.event_bus.publish(SetLightingEvent(
                    actuator_id=actuator.id,
                    color=tuple((lighting_color,) * 3 for _ in range(4)),
                    request_id="999"
                ))
            elif actuator.type == "fan":
                await self.event_bus.publish(SetFanStateEvent(
                    actuator_id=actuator.id,
                    fan_state=fan_state,
                    request_id="1000"
                ))


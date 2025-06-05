from loguru import logger
from typing import List

from src.domain.repositories import MqttCloudClientRepository, CacheClientRepository, HttpClientRepository
from src.domain.events import EventBusInterface, TelemetryEvent, SetLightingEvent, SetFanStateEvent
from src.domain.models import DeviceMode, DeviceStatus, Actuator, Device


LUMINOUSITY_MIN = 0.1
LUMINOUSITY_MAX = 0.8
TEMPERATURE_MIN = 0
TEMPERATURE_MAX = 100


class TelemetryService:
    def __init__(self, event_bus: EventBusInterface,
                 cache_client: CacheClientRepository,
                 cloud_client: MqttCloudClientRepository,
                 http_client: HttpClientRepository = None,
                 ):
        self.cache_client = cache_client
        self.cloud_client = cloud_client
        self.event_bus    = event_bus
        self.http_client = http_client

    async def start(self):
        await self.event_bus.subscribe(TelemetryEvent, self._handle_telemetry)
        logger.info("Telemetry service started")

    async def stop(self):
        await self.event_bus.unsubscribe(TelemetryEvent, self._handle_telemetry)
        logger.info("Telemetry service stopped")

    async def _handle_telemetry(self, event: TelemetryEvent):
        logger.info(f"Received telemetry event for device {event.device_id}")
        device = await self.cache_client.get_device_by_id(event.device_id)
        
        # Check if device was offline and set it to online
        if device.status == DeviceStatus.OFFLINE.value:
            logger.info(f"Device {device.name} was offline, setting to online")
            device_update = {"status": DeviceStatus.ONLINE.value}
            await self.cache_client.update_device(device.id, device_update)
            await self.http_client.set_device_status(device.id, DeviceStatus.ONLINE)
            # Update local device object to reflect the change
            device.status = DeviceStatus.ONLINE.value
        else:
            print(f"Device {device.name} is {device.status}")
            print(type(device.status))
            
        if device:
            try:
                logger.info(f"Handling telemetry for {device.name} with status {device.status}")
                # Check for error data and handle accordingly
                error_fields = [field for field, value in event.data.items() if value == "E"]
                
                if error_fields:
                    logger.warning(f"Device {device.name} reported error data in fields: {error_fields}")
                    
                    # Only update cache and backend if device was previously online
                    if device.status == DeviceStatus.ONLINE.value:
                        logger.info(f"Device {device.name} is online, updating status to ERROR")
                        device_update = {"status": DeviceStatus.ERROR.value}
                        await self.cache_client.update_device(device.id, device_update)
                        await self.http_client.set_device_status(device.id, DeviceStatus.ERROR)
                        # Update local device object to reflect the change
                        device.status = DeviceStatus.ERROR.value
                else:
                    print(f"Device {device.name} is {device.status} and type is {type(device.status)}")
                    if device.status == DeviceStatus.ERROR.value:
                        logger.info(f"Device {device.name} is error, updating status to ONLINE")
                        device_update = {"status": DeviceStatus.ONLINE.value}
                        await self.cache_client.update_device(device.id, device_update)
                        await self.http_client.set_device_status(device.id, DeviceStatus.ONLINE)
                        # Update local device object to reflect the change
                        device.status = DeviceStatus.ONLINE.value
                # Always send telemetry to cloud regardless of error status
                if device.status in [DeviceStatus.ONLINE.value, DeviceStatus.ERROR.value]:
                    self.cloud_client.send_telemetry(device.name, event.data)
                    
                    # Only handle auto actuator for non-error data
                    if not error_fields and device.status == DeviceStatus.ONLINE.value:
                        actuators = await self.cache_client.get_actuators_by_device_id(device.id)
                        await self._handle_auto_actuator(device, actuators, event.data)
                        
            except Exception as e:
                logger.error(f"Error processing telemetry from {device.name}: {e}")
        else:
            logger.error(f"Device not found: {event.device_id}")

    async def _handle_auto_actuator(self, device: Device, actuators: List[Actuator], data: dict):
        logger.info(f"Handling auto actuator for {device.name}")
        luminousity = data.get("luminousity")
        temperature = data.get("temperature")
        humidity = data.get("humidity")

        if luminousity == "E" or temperature == "E" or humidity == "E" or luminousity is None or temperature is None or humidity is None:
            await self.http_client.set_device_status(device.id, DeviceStatus.ERROR)
            logger.error(f"Device {device.name} reported error data in fields")
            return

        try:
            luminousity = float(luminousity)
            temperature = float(temperature)
            lighting_color = (LUMINOUSITY_MAX - luminousity) / (LUMINOUSITY_MAX - LUMINOUSITY_MIN) * 255
            lighting_color = max(0, min(lighting_color, 255))
            fan_state = temperature > 28

            for actuator in actuators:
                if actuator.mode == DeviceMode.AUTO.value:
                    if actuator.type == "led4RGB":
                        logger.info(f"Setting lighting color to {lighting_color}")
                        await self.event_bus.publish(SetLightingEvent(
                            actuator_id=actuator.id,
                            color=tuple((int(lighting_color),) * 3 for _ in range(4)),
                            request_id="-1",
                            waiting_response=False
                        ))
                    elif actuator.type == "fan":
                        await self.event_bus.publish(SetFanStateEvent(
                            actuator_id=actuator.id,
                            state=fan_state,
                            request_id="-1",
                            waiting_response=False
                        ))
        except Exception as e:
            logger.error(f"Error in auto actuator handling: {e}")


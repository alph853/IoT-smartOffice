import asyncio
from loguru import logger
from typing import List

from src.domain.repositories import MqttGatewayClientRepository, MqttCloudClientRepository
from src.domain.events import EventBusInterface, RegisterRequestEvent
from src.domain.models import Device, DeviceCreate
from src.domain.repositories import HttpClientRepository, CacheClientRepository


class RegistrationService:
    def __init__(self,
                 cloud_client: MqttCloudClientRepository,
                 gw_client: MqttGatewayClientRepository,
                 event_bus: EventBusInterface,
                 http_client: HttpClientRepository,
                 cache_client: CacheClientRepository,
                 gateway_id: int,
                 ):
        self.cloud_client = cloud_client
        self.gw_client    = gw_client
        self.event_bus    = event_bus
        self.http_client  = http_client
        self.cache_client = cache_client
        self.gateway_id   = gateway_id

    async def start(self):
        await self.event_bus.subscribe(RegisterRequestEvent, self.handle_register_request)

    async def stop(self):
        await self.event_bus.unsubscribe(RegisterRequestEvent, self.handle_register_request)

    async def handle_register_request(self, event: RegisterRequestEvent):
        """
        First send device provision request to the cloud,
        then request to backend server to update the database if needed
        and send the response to the device.
        """
        try:
            device = await self.cache_client.get_device_by_mac_addr(event.device.mac_addr)
            if device:
                logger.info(f"Device comebacks: {device}")
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self.http_client.update_device(device))
                    tg.create_task(self.cloud_client.connect_device(device))
            else:
                logger.info(f"Device not found: {event.device.model_dump()}")
                new_device = DeviceCreate(**event.device.model_dump(), gateway_id=self.gateway_id)
                new_device = await self.http_client.create_device(new_device)
                # if new_device:
                #     provision_device = await self.cloud_client.connect_device(new_device)
                #     device = await self.http_client.update_device(provision_device)
                #     await self.cache_client.add_device(device)
                # else:
                #     logger.error(f"Failed to create device {event.device.model_dump()}")
                #     return
            await self.gw_client.register_device(new_device)
        except Exception as e:
            logger.error(f"Error in registration service: {e}")
            return

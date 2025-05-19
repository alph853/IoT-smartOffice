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
        try:
            event.device.gateway_id = self.gateway_id
            device = await self.http_client.connect_device(event.device)
            self.cloud_client.connect_device(device),
            tasks = await asyncio.gather(
                self.cache_client.add_device(device),
                self.gw_client.register_device(device),
                return_exceptions=True
            )
            for index, task in enumerate(tasks):
                if isinstance(task, Exception):
                    logger.error(f"Error in registration service {index}: {task}")
        except Exception as e:
            logger.error(f"Error in registration service: {e}")
            return


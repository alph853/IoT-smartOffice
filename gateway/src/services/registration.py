from loguru import logger
from typing import List

from src.domain.repositories import MqttGatewayClientRepository, MqttCloudClientRepository
from src.domain.events import EventBusInterface, RegisterRequestEvent
from src.domain.models import Device


class RegistrationService:
    def __init__(self,
                 cloud_client: MqttCloudClientRepository,
                 gw_client: MqttGatewayClientRepository,
                 event_bus: EventBusInterface,
                 ):
        self.cloud_client = cloud_client
        self.gw_client = gw_client
        self.event_bus   = event_bus

        self.devices: List[Device] = []

    async def subscribe_events(self):
        await self.event_bus.subscribe(RegisterRequestEvent, self.handle_register_request)

    async def handle_register_request(self, event: RegisterRequestEvent):
        logger.info(f"Received register request: {event.model_dump()}")
        await self.gw_client.publish(event.topic, event.payload)
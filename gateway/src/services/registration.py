from loguru import logger
from typing import List

from src.domain.repositories import MqttGatewayClientRepository, MqttCloudClientRepository
from src.domain.events import EventBusInterface, RegisterRequestEvent
from src.domain.models import Device, MqttTopic, Topic
from src.domain.repositories import HttpClientRepository


class RegistrationService:
    def __init__(self,
                 cloud_client: MqttCloudClientRepository,
                 gw_client: MqttGatewayClientRepository,
                 event_bus: EventBusInterface,
                 topics: List[MqttTopic],
                 http_client: HttpClientRepository
                 ):
        self.cloud_client = cloud_client
        self.gw_client    = gw_client
        self.event_bus    = event_bus
        self.http_client  = http_client

        self.regresp_topic = next(filter(lambda t:
             t.topic == Topic.REGISTER_RESPONSE, topics))

    async def start(self):
        response = await self.http_client.send_request(
            url=f"{self.config.backend.url}{self.config.backend.all_devices_api}",
            method="GET",
            headers={
                "Content-Type": "application/json"
            }
        )
        logger.info(f"All devices: {response}")
        await self.event_bus.subscribe(RegisterRequestEvent, self.handle_register_request)

    async def handle_register_request(self, event: RegisterRequestEvent):
        """
        First send device provision request to the cloud,
        then request to backend server to update the database if needed
        and send the response to the device.
        """
        logger.info(f"Received register request: {event.model_dump()}")
        await self.cloud_client
        await self.gw_client.publish(self.regresp_topic, event.model_dump())
        await self.http_client.send_request(
            url=f"{self.config.thingsboard.url}/api/v1/devices/me/rpc/request",
            payload=event.model_dump()
        )
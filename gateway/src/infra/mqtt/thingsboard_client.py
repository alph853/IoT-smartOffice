from typing import List
from aiomqtt import Client, Message, MessagesIterator
import asyncio
from loguru import logger

from src.domain.events import EventBusInterface
from src.domain.models import MqttTopic, Entity
from src.domain.repositories import MqttCloudClientRepository
from tb_gateway_mqtt import TBGatewayMqttClient


class ThingsboardClient(MqttCloudClientRepository):
    def __init__(self, broker_url: str,
                 password: str,
                 topics: List[MqttTopic],
                 event_bus: EventBusInterface,
                 broker_port: int = 1883,
                 client_id: str = "",
                 username: str = "",
                 ):

        self.broker_url  = broker_url
        self.broker_port = broker_port
        self.client_id   = client_id
        self.username    = username
        self.password    = password
        self.event_bus   = event_bus

        self.client = None
        self.subscribed_topics = list(filter(lambda t:
            t.src == Entity.CLOUD and t.dst == Entity.GATEWAY,
            topics
        ))

    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    async def connect(self):
        self.client = TBGatewayMqttClient(
            host=self.broker_url,
            port=self.broker_port,
            username=self.username,
            password=self.password,
            client_id=self.client_id,
        )
        await self.client.__aenter__()

        subscription_tasks = [
            self.client.subscribe(topic=(topic.topic, topic.retain), qos=topic.qos)
            for topic in self.subscribed_topics
        ]
        await asyncio.gather(*subscription_tasks)
        logger.info(f"Subscribed to {len(self.subscribed_topics)} topics")
        logger.info(f"Thingsboard broker connected at {self.broker_url}:{self.broker_port}.")

    async def disconnect(self):
        await self.client.__aexit__(None, None, None)
        logger.info(f"Thingsboard broker disconnected.")

    @property
    def messages(self) -> MessagesIterator:
        return self.client.messages

    # -------------------------------------------------------------
    # ------------------------- Publish -------------------------
    # -------------------------------------------------------------

    async def publish(self, topic: MqttTopic, payload: str):
        await self.client.publish(topic.topic, payload, topic.qos, topic.retain)
    
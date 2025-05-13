from typing import List
import socket
from aiomqtt import Client, Message, MessagesIterator
from loguru import logger
import asyncio

from src.domain.models import MqttTopic, Entity
from src.domain.events import EventBusInterface
from src.domain.repositories import MqttGatewayClientRepository


class MosquittoClient(MqttGatewayClientRepository):
    def __init__(self, broker_url: str, broker_port: int,
                 event_bus: EventBusInterface, topics: List[MqttTopic]):
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.event_bus = event_bus

        self.client = None
        self.subscribed_topics = list(filter(lambda t:
            t.src == Entity.DEVICE and t.dst == Entity.GATEWAY,
            topics
        ))
        self.published_topics = list(filter(lambda t:
            t.src == Entity.GATEWAY and t.dst == Entity.DEVICE,
            topics
        ))

    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    async def connect(self):
        if not self._is_broker_running():
            logger.error(f"Broker is not running at {self.broker_url}:{self.broker_port}")
            return

        self.client = Client(self.broker_url, self.broker_port)
        await self.client.__aenter__()
        subscription_tasks = [
            self.client.subscribe(topic=(topic.topic, topic.retain), qos=topic.qos)
            for topic in self.subscribed_topics
        ]
        await asyncio.gather(*subscription_tasks)
        logger.info(f"Subscribed to {len(self.subscribed_topics)} topics")
        logger.info(f"Mosquitto broker connected at {self.broker_url}:{self.broker_port}.")

    async def disconnect(self):
        await self.client.__aexit__(None, None, None)
        logger.info(f"Mosquitto broker disconnected.")

    @property
    def messages(self) -> MessagesIterator:
        """Get the messages stream for the listener."""
        return self.client.messages

    # -------------------------------------------------------------
    # ------------------------- Publisher -------------------------
    # -------------------------------------------------------------

    async def publish(self, topic: str, payload: str):
        topic = next(filter(lambda t: t.topic.value == topic, self.published_topics))
        await self.client.publish(topic.topic.value, payload, topic.qos, topic.retain)

    # -------------------------------------------------------------
    # ------------------------- Utilities -------------------------
    # -------------------------------------------------------------

    def _is_broker_running(self):
        """Check if a broker is running at the specified host and port."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.broker_url, self.broker_port))
            sock.close()
            return True
        except:
            sock.close()
            return False

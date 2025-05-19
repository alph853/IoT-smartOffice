from typing import List
import socket
from aiomqtt import Client, Message, MessagesIterator, MqttError
from loguru import logger
import asyncio
import json
from typing import Dict, Any

from src.domain.models import DeviceRegistration, Device
from src.domain.repositories import MqttGatewayClientRepository, CacheClientRepository

from src.domain.events import (
    EventBusInterface, RegisterRequestEvent, TelemetryEvent, ControlResponseEvent,
    InvalidMessageEvent, TestEvent
)


class MosquittoClient(MqttGatewayClientRepository):
    def __init__(self,
                 broker_url: str,
                 broker_port: int,
                 event_bus: EventBusInterface,
                 cache_client: CacheClientRepository,
                 topics: Dict[str, Dict[str, Any]]
                 ):
        self.broker_url  = broker_url
        self.broker_port = broker_port
        self.event_bus   = event_bus
        self.cache_client = cache_client
        self.topics      = topics

        self.client = None


    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    async def connect(self):
        if not self._is_broker_running():
            logger.error(f"Broker is not running at {self.broker_url}:{self.broker_port}")
            return

        self.client = Client(self.broker_url, self.broker_port)
        await self.client.__aenter__()

        await self._startup()

    async def disconnect(self):
        await self.client.__aexit__(None, None, None)
        if not self._listener_task.done():
            self._listener_task.cancel()

        logger.info(f"Mosquitto broker disconnected.")

    # -------------------------------------------------------------
    # ------------------------- Publisher -------------------------
    # -------------------------------------------------------------

    async def register_device(self, device: Device):
        topics = "telemetry", "control_response"
        topics_info = [self.topics[topic] for topic in topics]
        subscription_tasks = [
            self.client.subscribe(topic=(topic['topic'] + str(device.id), topic['retain']), qos=topic['qos'])
            for topic in topics_info
        ]
        await asyncio.gather(*subscription_tasks)

        topic = self.topics['register_response']['topic'].format(device_id=device.mac_addr)
        print(f"Registering device {device.id} to topic {topic}")
        await self.client.publish(topic, f"OK,id={device.id}")

    async def connect_device(self, device: Device):
        topics = "telemetry", "control_response"
        topics_info = [self.topics[topic] for topic in topics]
        subscription_info = [{
                "topic": topic['topic'] + str(device.id),
                "qos": topic['qos'],
                "retain": topic['retain']
            } for topic in topics_info
        ]
        await self._subscribe_topics(subscription_info)

        logger.info(f"Connected device {device.id}")

    async def disconnect_device(self, device: Device):
        topics = "telemetry", "control_response"
        topics_info = [self.topics[topic] for topic in topics]
        topics = [topic['topic'] + str(device.id) for topic in topics_info]
        await self._unsubscribe_topics(topics)

        logger.info(f"Disconnected device {device.id}")


    # -------------------------------------------------------------
    # ------------------------- Listener --------------------------
    # -------------------------------------------------------------

    async def _listen(self):
        """Listen for MQTT messages"""
        try:
            logger.info("Mosquitto MQTT listener started")
            async for msg in self.client.messages:
                await self._process_message(msg)
        except asyncio.CancelledError:
            pass
        except MqttError as e:
            logger.error(f"Connection lost ({e}); Reconnecting...")
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error in Mosquitto MQTT listener: {e}")
        finally:
            logger.info("Mosquitto MQTT listener stopped")

    async def _process_message(self, msg: Message):
        """Process a single MQTT message"""
        topic = str(msg.topic)
        payload = msg.payload.decode()

        logger.info(f"Received message on topic {topic}: {payload}")

        if topic.startswith(self.topics['test']['topic']):
            event = TestEvent(payload=payload)
            await self.event_bus.publish(event)
            return
        try:
            payload = json.loads(payload)
        except Exception:
            event = InvalidMessageEvent(topic=str(topic), payload=payload, error="JSON parsing error")
        else:
            if topic.startswith(self.topics['register_request']['topic']):
                event = RegisterRequestEvent(device=DeviceRegistration(**payload))
            elif topic.startswith(self.topics['telemetry']['topic']):
                device_id = topic.split('/')[-1]
                event = TelemetryEvent(device_id=device_id, data=payload)
            elif topic.startswith(self.topics['control_response']['topic']):
                event = ControlResponseEvent(**payload)
            else:
                event = InvalidMessageEvent(topic=str(topic), payload=str(payload), error="Not implemented error")
        finally:
            await self.event_bus.publish(event)

    async def _handle_test_connection(self, event: TestEvent):
        logger.info(f'Received test message on "{event.payload}"')

    async def _handle_invalid_message(self, event: InvalidMessageEvent):
        logger.error(f'Received invalid message on "{event.topic}": "{event.payload}"')


    # -------------------------------------------------------------
    # ------------------------- Helper ----------------------------
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

    async def _startup(self):
        devices = await self.cache_client.get_all_devices()
        for device in devices:
            if device.status == "online":
                await self.connect_device(device)

        subscribed_topics = ["test", "register_request",]
        subscribed_topic_info = [self.topics[topic] for topic in subscribed_topics]
        await self._subscribe_topics(subscribed_topic_info)

        logger.info(f"Subscribed to {len(subscribed_topics)} topics:\n'{'\n'.join([t['topic'] for t in subscribed_topic_info])}'")
        logger.info(f"Mosquitto broker connected at {self.broker_url}:{self.broker_port}.")

        await self.event_bus.subscribe(TestEvent, self._handle_test_connection)
        await self.event_bus.subscribe(InvalidMessageEvent, self._handle_invalid_message)
        self._listener_task = asyncio.create_task(self._listen())

    async def _subscribe_topics(self, subscribed_topic_info: List[Dict[str, Any]]):
        subscription_tasks = [
            self.client.subscribe(topic=(topic['topic'], topic['retain']), qos=topic['qos'])
            for topic in subscribed_topic_info
        ]
        await asyncio.gather(*subscription_tasks)
        logger.info(f"Subscribing to {len(subscribed_topic_info)} topics: \n{'\n'.join([t['topic'] for t in subscribed_topic_info])}")

    async def _unsubscribe_topics(self, topics: List[str]):
        subscription_tasks = [self.client.unsubscribe(topic) for topic in topics]
        await asyncio.gather(*subscription_tasks)
        logger.info(f"Unsubscribed from {len(topics)} topics: \n{'\n'.join(topics)}")
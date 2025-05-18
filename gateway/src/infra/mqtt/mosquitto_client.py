from typing import List
import socket
from aiomqtt import Client, Message, MessagesIterator, MqttError
from loguru import logger
import asyncio
import json
from typing import Dict, Any

from src.domain.models import DeviceRegistration, Device
from src.domain.repositories import MqttGatewayClientRepository

from src.domain.events import (
    EventBusInterface, RegisterRequestEvent, TelemetryEvent, ControlResponseEvent,
    InvalidMessageEvent, TestEvent
)


class MosquittoClient(MqttGatewayClientRepository):
    def __init__(self,
                 broker_url: str,
                 broker_port: int,
                 event_bus: EventBusInterface,
                 topics: Dict[str, Dict[str, Any]]
                 ):
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.event_bus = event_bus
        self.topics = topics

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

        subscribed_topics = list(filter(lambda i:
            i['src'] == "device" and i['dst'] == "gateway",
            self.topics.values()
        ))
        subscription_tasks = [
            self.client.subscribe(topic=(topic['topic'], topic['retain']), qos=topic['qos'])
            for topic in subscribed_topics
        ]
        await asyncio.gather(*subscription_tasks)

        logger.info(f"Subscribed to {len(subscribed_topics)} topics:\n'{'\n'.join([t['topic'] for t in subscribed_topics])}'")
        logger.info(f"Mosquitto broker connected at {self.broker_url}:{self.broker_port}.")

        await self.event_bus.subscribe(TestEvent, self._handle_test_connection)
        await self.event_bus.subscribe(InvalidMessageEvent, self._handle_invalid_message)
        self._listener_task = asyncio.create_task(self._listen())

    async def disconnect(self):
        await self.client.__aexit__(None, None, None)
        if not self._listener_task.done():
            self._listener_task.cancel()

        logger.info(f"Mosquitto broker disconnected.")

    # -------------------------------------------------------------
    # ------------------------- Publisher -------------------------
    # -------------------------------------------------------------

    async def publish(self, topic: str, payload: str):
        await self.client.publish(topic, payload, topic.qos, topic.retain)

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

    async def register_device(self, device: Device):
        topic = self.topics['register_response']['topic'].format(device_id=device.mac_addr)
        print(f"Registering device {device.mac_addr} with id {device.id} to topic {topic}")
        await self.client.publish(topic, f"OK,id={device.id}")

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
        topic = msg.topic
        payload = msg.payload.decode()

        logger.info(f"Received message on topic {topic}: {payload}")

        if topic.matches(self.topics['test']['topic']):
            event = TestEvent(payload=payload)
            await self.event_bus.publish(event)
            return
        try:
            payload = json.loads(payload)
        except Exception:
            event = InvalidMessageEvent(topic=str(topic), payload=payload, error="JSON parsing error")
        else:
            if topic.matches(self.topics['register_request']['topic']):
                event = RegisterRequestEvent(device=DeviceRegistration(**payload))
            elif topic.matches(self.topics['telemetry']['topic']):
                event = TelemetryEvent(**payload)
            elif topic.matches(self.topics['control_response']['topic']):
                event = ControlResponseEvent(**payload)
            else:
                event = InvalidMessageEvent(topic=str(topic), payload=str(payload), error="Not implemented error")
        finally:
            await self.event_bus.publish(event)

    async def _handle_test_connection(self, event: TestEvent):
        logger.info(f'Received test message on "{event.payload}"')

    async def _handle_invalid_message(self, event: InvalidMessageEvent):
        logger.error(f'Received invalid message on "{event.topic}": "{event.payload}"')

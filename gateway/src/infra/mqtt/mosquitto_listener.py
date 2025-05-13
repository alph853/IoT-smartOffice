import json
from aiomqtt import Message, MqttError, MessagesIterator
from typing import List
import asyncio
from loguru import logger

from src.domain.events import (
    EventBusInterface, RegisterRequestEvent, TelemetryEvent, ControlResponseEvent,
    InvalidMessageEvent, TestEvent
)
from src.domain.models import Topic


class MosquittoListener:
    def __init__(self, msg_generator: MessagesIterator,
                 event_bus: EventBusInterface):
        self.msg_generator = msg_generator
        self.event_bus = event_bus
        self.listener_task = None

    async def start(self):
        """Start listening for MQTT messages"""
        await self.event_bus.subscribe(TestEvent, self._handle_test_connection)
        self.listener_task = asyncio.create_task(self._listen())

    async def stop(self):
        """Gracefully stop the MQTT listener"""
        if not self.listener_task.done():
            self.listener_task.cancel()
        logger.info("MQTT listener stopped")

    async def _listen(self):
        """Listen for MQTT messages"""
        try:
            logger.info("MQTT listener started")
            async for msg in self.msg_generator:
                await self._process_message(msg)
        except asyncio.CancelledError:
            pass
        except MqttError as e:
            logger.error(f"Connection lost ({e}); Reconnecting...")
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error in MQTT listener: {e}")
        finally:
            logger.info("MQTT listener stopped")

    async def _process_message(self, msg: Message):
        """Process a single MQTT message"""
        topic = msg.topic
        payload = msg.payload.decode()

        if topic.matches(Topic.TEST.value):
            event = TestEvent(payload=payload)
            await self.event_bus.publish(event)
            return

        try:
            payload = json.loads(payload)
        except Exception as e:
            event = InvalidMessageEvent(topic, payload, str(e))
        else:
            if topic.matches(Topic.REGISTER_REQUEST.value):
                event = RegisterRequestEvent(**payload)
            elif topic.matches(Topic.TELEMETRY.value):
                event = TelemetryEvent(**payload)
            elif topic.matches(Topic.CONTROL_RESPONSE.value):
                event = ControlResponseEvent(**payload)
            else:
                event = InvalidMessageEvent(topic, payload, "Not implemented error")
        finally:
            await self.event_bus.publish(event)

    async def _handle_test_connection(self, event: TestEvent):
        logger.info(f'Received test message on "{event.payload}"')

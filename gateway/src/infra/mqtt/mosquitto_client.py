from typing import List
import socket
from aiomqtt import Client, Message, MessagesIterator, MqttError
from loguru import logger
import asyncio
import json
from typing import Dict, Any

from src.domain.models import DeviceRegistration, Device, Actuator, DeviceMode
from src.domain.repositories import MqttGatewayClientRepository, CacheClientRepository
from src.domain.events import (
    EventBusInterface, RegisterRequestEvent, TelemetryEvent, ControlResponseEvent,
    InvalidMessageEvent, TestEvent, SetLightingEvent, SetFanStateEvent, RPCTestEvent
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

        self.pending_requests = {}
        self.client = None
        self.handlers = {
            TestEvent: self._handle_test_connection,
            InvalidMessageEvent: self._handle_invalid_message,
        }
        self.topic_callbacks = {}  # Store callbacks for specific topics


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
    # ------------------------- Subscriber ------------------------
    # -------------------------------------------------------------
    
    async def get_topics(self) -> Dict[str, Dict[str, Any]]:
        """Get all configured topics"""
        return self.topics
    
    async def subscribe(self, topic: str, callback):
        """Subscribe to a specific topic with a callback"""
        # Add callback to event handlers
        # For LWT, we'll handle it in the message processor
        self.topic_callbacks[topic] = callback
        await self.client.subscribe(topic=topic, qos=1)
        logger.info(f"Subscribed to topic: {topic}")
    
    async def unsubscribe(self, topic: str):
        """Unsubscribe from a specific topic"""
        await self.client.unsubscribe(topic)
        self.topic_callbacks.pop(topic, None)
        logger.info(f"Unsubscribed from topic: {topic}")

    # -------------------------------------------------------------
    # ------------------------- Publisher -------------------------
    # -------------------------------------------------------------

    async def register_device(self, device: Device):
        topics = "telemetry", "control_response"
        topics_info = [self.topics[topic] for topic in topics]
        print(f"Subscribing to {len(topics_info)} topics: \n{'\n'.join([t['topic'] + str(device.id) for t in topics_info])}")
        subscription_tasks = [
            self.client.subscribe(topic=(topic['topic'] + str(device.id), topic['retain']), qos=topic['qos'])
            for topic in topics_info
        ]
        await asyncio.gather(*subscription_tasks)

        response_data = {
            "status": "OK",
            "device_id": device.id,
            "sensors": [{"name": sensor.name, "id": i} for i, sensor in enumerate(device.sensors)] if device.sensors else [],
            "actuators": [{"name": actuator.name, "id": i} for i, actuator in enumerate(device.actuators)] if device.actuators else []
        }

        topic = self.topics['register_response']['topic'].format(device_id=device.mac_addr.replace(":", ""))
        logger.info(f"Registering device {device.id} to topic {topic}")
        await self.client.publish(topic, json.dumps(response_data))

    async def connect_device(self, device_id: int):
        topics = "telemetry", "control_response"
        topics_info = [self.topics[topic] for topic in topics]
        subscription_info = [{
                "topic": topic['topic'] + str(device_id),
                "qos": topic['qos'],
                "retain": topic['retain']
            } for topic in topics_info
        ]
        await self._subscribe_topics(subscription_info)

        logger.info(f"Connected device {device_id}")

    async def disconnect_device(self, device_id: int):
        topics = "telemetry", "control_response"
        topics_info = [self.topics[topic] for topic in topics]
        topics = [topic['topic'] + str(device_id) for topic in topics_info]
        await self._unsubscribe_topics(topics)

        logger.info(f"Disconnected device {device_id}")

    async def set_lighting(self, event: SetLightingEvent) -> bool:
        payload = {
            "method": "setLighting",
            "params": event.model_dump()
        }
        device_id = await self.cache_client.get_device_id_by_actuator_id(event.actuator_id)
        if device_id:
            topic = self.topics['control_commands']['topic'].format(device_id=device_id)
            await self.client.publish(topic, json.dumps(payload))
            return await self._wait_for_response(event.request_id)
        return False

    async def set_fan_state(self, event: SetFanStateEvent) -> bool:
        payload = {
            "method": "setFanState",
            "params": event.model_dump()
        }
        device_id = await self.cache_client.get_device_id_by_actuator_id(event.actuator_id)
        if not device_id:
            return False
        topic = self.topics['control_commands']['topic'].format(device_id=device_id)
        await self.client.publish(topic, json.dumps(payload))
        return await self._wait_for_response(event.request_id)

    async def send_test_command(self, event: RPCTestEvent) -> bool:
        payload = {
            "method": "test",
            "params": event.model_dump()
        }
        device_id = await self.cache_client.get_device_id_by_actuator_id(event.actuator_id)
        if not device_id:
            return False
        topic = self.topics['control_commands']['topic'] + str(device_id)
        await self.client.publish(topic, json.dumps(payload))
        return await self._wait_for_response(event.request_id)


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
        
        # Check if there's a specific callback for this topic
        if topic in self.topic_callbacks:
            try:
                await self.topic_callbacks[topic]({"topic": topic, "payload": payload})
                return
            except Exception as e:
                logger.error(f"Error in topic callback for {topic}: {e}")
                return
        
        try:
            try:    payload = json.loads(payload)
            except: payload = payload

            if topic.startswith(self.topics['test']['topic']):
                event = TestEvent(payload=payload)
            elif topic == self.topics.get('lwt', {}).get('topic'):
                # Handle LWT message
                event = None
                if 'lwt' in self.topic_callbacks:
                    await self.topic_callbacks['lwt']({"topic": topic, "payload": payload})
            elif topic.startswith(self.topics['register_request']['topic']):
                event = RegisterRequestEvent(device=DeviceRegistration(**payload))
            elif topic.startswith(self.topics['telemetry']['topic']):
                device_id = topic.split('/')[-1]
                event = TelemetryEvent(device_id=device_id, data=payload)
            elif topic.startswith(self.topics['control_response']['topic']):
                event = None
                request_id = payload.get('request_id')
                if request_id and request_id in self.pending_requests:
                    print(self.pending_requests)
                    future = self.pending_requests[request_id]
                    if not future.done():
                        if payload.get('status') == 'success':
                            future.set_result(True)
                        else:
                            future.set_result(False)
                    else:
                        print(222)
            else:
                event = InvalidMessageEvent(topic=str(topic), payload=str(payload), error="Not implemented error")
        except Exception as e:
            event = InvalidMessageEvent(topic=str(topic), payload=str(payload), error=str(e))
        finally:
            if event:
                await self.event_bus.publish(event)

    async def _handle_test_connection(self, event: TestEvent):
        logger.info(f'Received test message on "{event.payload}"')

    async def _handle_invalid_message(self, event: InvalidMessageEvent):
        logger.error(f'Received invalid message on "{event.topic}": "{event.payload}\nError:{event.error}"')


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
                await self.connect_device(device.id)

        subscribed_topics = ["test", "register_request",]
        subscribed_topic_info = [self.topics[topic] for topic in subscribed_topics]
        await self._subscribe_topics(subscribed_topic_info)

        logger.info(f"Subscribed to {len(subscribed_topics)} topics:\n'{'\n'.join([t['topic'] for t in subscribed_topic_info])}'")
        logger.info(f"Mosquitto broker connected at {self.broker_url}:{self.broker_port}.")

        await asyncio.gather(
            *[self.event_bus.subscribe(event, handler) for event, handler in self.handlers.items()]
        )
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

    async def _wait_for_response(self, request_id: str) -> bool:
        response_future = asyncio.Future()
        self.pending_requests[request_id] = response_future

        try:
            result = await asyncio.wait_for(response_future, timeout=8.0)
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for response to request {request_id}")
            return False
        finally:
            self.pending_requests.pop(request_id, None)

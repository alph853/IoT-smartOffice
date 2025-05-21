from typing import List, Dict, Any
from aiomqtt import Client, Message, MessagesIterator
import asyncio
from loguru import logger

from src.domain.events import *
from src.domain.repositories import MqttCloudClientRepository, CacheClientRepository, MqttGatewayClientRepository
from src.domain.models import Device
from tb_gateway_mqtt import TBGatewayMqttClient


class ThingsboardClient(MqttCloudClientRepository):
    def __init__(self, broker_url: str,
                 event_bus: EventBusInterface,
                 password: str,
                 broker_port: int = 1883,
                 client_id: str = "",
                 username: str = "",
                 device_name: str = "",
                 topics: Dict[str, Dict[str, Any]] = {},
                 loop: asyncio.AbstractEventLoop = None,
                 ):

        self.broker_url   = broker_url
        self.broker_port  = broker_port
        self.client_id    = client_id
        self.username     = username
        self.password     = password
        self.event_bus    = event_bus
        self.device_name  = device_name

        self.client = None
        self.topics = topics
        self.loop   = loop
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
        self.client.connect()
        self.client.gw_subscribe_to_all_attributes(self.attribute_callback)
        self.client.set_server_side_rpc_request_handler(self.rpc_callback)

    async def disconnect(self):
        self.client.disconnect()
        logger.info(f"Thingsboard broker disconnected.")

    # -------------------------------------------------------------
    # ------------------------- Publish -------------------------
    # -------------------------------------------------------------

    def connect_device(self, device: Device):
        return self.client.gw_connect_device(device.name)

    def disconnect_device(self, device: Device):
        return self.client.gw_disconnect_device(device.name)

    def send_telemetry(self, device: str, telemetry: dict, qos: int = 1):
        logger.info(f"Sending telemetry to {device} with {telemetry}")
        return self.client.gw_send_telemetry(device, telemetry, qos)

    def send_attributes(self, device: str, attributes: dict, qos: int = 1):
        return self.client.gw_send_attributes(device, attributes, qos)

    def send_rpc_reply(self, request_id: str, response: dict, device: str | None = None, qos: int = 1):
        if not device:
            device = self.device_name
        return self.client.gw_send_rpc_reply(device, request_id, response, qos)

    # -------------------------------------------------------------
    # ------------------------- Callback -------------------------
    # -------------------------------------------------------------

    def attribute_callback(self, device, key, value):
        logger.info(f"Attribute {key} of device {device} has been updated to {value}")

    def rpc_callback(self, request_id, content):
        logger.info(f"RPC {request_id} has been called with params {content}")
        task = self.loop.create_task(self._handle_rpc_async(request_id, content))
        task.add_done_callback(self._handle_rpc_task_done)

    def _handle_rpc_task_done(self, task):
        try:
            task.result()
            logger.info(f"RPC has been handled successfully")
        except Exception as e:
            logger.error(f"Error in RPC task: {str(e)}", exc_info=True)

    async def _handle_rpc_async(self, request_id, content):
        event = None
        method = content.get("method")
        params = content.get("params", {})

        try:
            if method == "deleteDevice":
                event = DeleteDeviceEvent(**params)
                await self.event_bus.publish(event)
            elif method == "updateDevice":
                event = UpdateDeviceEvent(**params)
                await self.event_bus.publish(event)
            elif method == "gateway_device_deleted":
                event = GatewayDeviceDeletedEvent(request_id=request_id)
                await self.event_bus.publish(event)
            elif method == "updateActuator":
                event = UpdateActuatorEvent(**params)
                await self.event_bus.publish(event)
            elif method == "setMode":
                event = SetModeEvent(**params)
                await self.event_bus.publish(event)
            elif method == "setLighting":
                event = SetLightingEvent(**params)
                await self.event_bus.publish(event)
            elif method == "setFanState":
                event = SetFanStateEvent(**params)
                await self.event_bus.publish(event)
            elif method == "test":
                event = RPCTestEvent(**params)
                await self.event_bus.publish(event)
            else:
                event = UnknownEvent(**params)
                await self.event_bus.publish(event)
        except Exception as e:
            logger.error(f"Error in RPC task: {str(e)}")
            event = InvalidRPCEvent(params=params, method=method)
        finally:
            event.request_id = request_id
            await self.event_bus.publish(event)

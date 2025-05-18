from typing import List, Dict, Any
from aiomqtt import Client, Message, MessagesIterator
import asyncio
from loguru import logger

from src.domain.events import EventBusInterface
from src.domain.repositories import MqttCloudClientRepository, CacheClientRepository
from src.domain.models import RPCResponse, Device
from tb_gateway_mqtt import TBGatewayMqttClient


class ThingsboardClient(MqttCloudClientRepository):
    def __init__(self, broker_url: str,
                 event_bus: EventBusInterface,
                 cache_client: CacheClientRepository,
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
        self.cache_client = cache_client

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
        return self.client.gw_send_telemetry(device, telemetry, qos)

    def send_attributes(self, device: str, attributes: dict, qos: int = 1):
        return self.client.gw_send_attributes(device, attributes, qos)

    def send_rpc_reply(self, device: str, method: str, params: dict, qos: int = 1):
        return self.client.gw_send_rpc_reply(device, method, params, qos)

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
        method = content.get("method")
        params = content.get("params", {})

        response = None

        if method == "disconnectDevice":
            device_id = params.get("device_id")
            device = await self.cache_client.get_device_by_id(device_id)
            if device:
                if await self.cache_client.remove_device(device_id):
                    response = RPCResponse(status="success", data={"message": "Device disconnected"})
                    self.disconnect_device(device)
            else:
                response = RPCResponse(status="error", data={"message": "Device not found"})
        else:
            response = RPCResponse(status="error", data={"message": "RPC method not found"})

        if not response:
            response = RPCResponse(status="error", data={"message": "There is an error in the RPC method"})
        
        logger.info(f"Sending RPC reply for {self.device_name} with request_id {request_id} and response {response.model_dump()}")
        self.send_rpc_reply(self.device_name, request_id, response.model_dump(), 1)

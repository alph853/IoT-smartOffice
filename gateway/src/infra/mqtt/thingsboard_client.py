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

    async def connect_device(self, device: str):
        return self.client.gw_connect_device(device)

    async def disconnect_device(self, device: str):
        return self.client.gw_disconnect_device(device)

    async def send_telemetry(self, device: str, telemetry: dict, qos: int = 1):
        return self.client.gw_send_telemetry(device, telemetry, qos)

    async def send_attributes(self, device: str, attributes: dict, qos: int = 1):
        return self.client.gw_send_attributes(device, attributes, qos)

    async def send_rpc_reply(self, device: str, method: str, params: dict, qos: int = 1):
        return self.client.gw_send_rpc_reply(device, method, params, qos)

    # -------------------------------------------------------------
    # ------------------------- Callback -------------------------
    # -------------------------------------------------------------

    async def attribute_callback(self, device, key, value):
        logger.info(f"Attribute {key} of device {device} has been updated to {value}")

    async def rpc_callback(self, device, method, params):
        logger.info(f"RPC {method} of device {device} has been called with params {params}")

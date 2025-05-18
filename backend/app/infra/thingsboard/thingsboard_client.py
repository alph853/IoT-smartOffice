import json
import asyncio
from typing import Dict, Any, Optional
from tb_gateway_mqtt import TBGatewayMqttClient
import websockets
from loguru import logger

from app.domain.events import EventBusInterface
from app.domain.repositories import MqttCloudClientRepository, HttpClientRepository
from app.domain.models import RPCResponse, ModeSet, LightingSet, Device


class ThingsboardClient(MqttCloudClientRepository):
    def __init__(self, event_bus: EventBusInterface,
                 http_client: HttpClientRepository,
                 broker_url: str,
                 broker_port: int = 1883,
                 client_id: str = "",
                 username: str = "",
                 password: str = "",
                 device_id: str = "",
                 device_name: str = "",
                 api: dict = {}
                 ):

        self.http_client = http_client
        self.event_bus = event_bus

        self.broker_url = broker_url
        self.broker_port = broker_port
        self.client_id = client_id
        self.username = username
        self.password = password

        self.device_id = device_id
        self.device_name = device_name
        self.api = api

        self._jwt = None

    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    async def connect(self):
        self._jwt = await self._get_jwt()
        self.headers = self._get_headers_with_jwt()
        self._ws_listener_task = asyncio.create_task(self._thingsboard_ws_listener())
        logger.info(f"Thingsboard WS connected!")

    async def disconnect(self):
        if not self._ws_listener_task.done():
            self._ws_listener_task.cancel()
        logger.info(f"Thingsboard broker disconnected.")

    # -------------------------------------------------------------
    # ------------------------- Listeners -------------------------
    # -------------------------------------------------------------

    async def _thingsboard_ws_listener(self):
        ws_url = self.api.ws_url + self._jwt
        try:
            async with websockets.connect(ws_url) as ws:
                logger.info(f"Thingsboard WS listener started!")
                try:
                    subscription_req = {
                        "tsSubCmds": [
                            {
                                "entityType": "DEVICE",
                                "entityId": self.device_id,
                                "scope": "LATEST_TELEMETRY",
                                "cmdId": 10,
                                "type": "TIMESERIES"
                            },
                            {
                                "entityType": "DEVICE",
                                "entityId": self.device_id,
                                "scope": "LATEST_TELEMETRY",
                                "cmdId": 11,
                                "type": "NOTIFICATIONS"
                            }
                        ]
                    }
                    await ws.send(json.dumps(subscription_req))

                    async for message in ws:
                        try:
                            logger.info(f"Received message: {message}")
                            message_json = json.loads(message)
                            logger.info(f"Parsed message: {message_json}")
                        except json.JSONDecodeError as e:
                            logger.error(f"Received non-JSON message: {message}, error: {e}")
                        except Exception as e:
                            logger.error(f"Error processing telemetry: {e}")
                except websockets.ConnectionClosed as e:
                    logger.error(f"Thingsboard WS session closed: {e.code} - {e}")
                except Exception as e:
                    logger.error(f"Thingsboard WS connection error: {e}")
                finally:
                    logger.info("Thingsboard WS listener closed.")
        except Exception as e:
            logger.error(f"Failed to establish Thingsboard WS connection: {e}")

    # -------------------------------------------------------------
    # ----------------------------- RPC ---------------------------
    # -------------------------------------------------------------

    async def set_mode(self, request: ModeSet) -> RPCResponse:
        logger.info(f"Setting mode to {request.params}")
        url = self.api.rpc.format(device_id=self.device_id)
        await self.http_client.request(url, payload=request.model_dump(), method="POST")

    async def set_lighting(self, request: LightingSet) -> RPCResponse:
        logger.info(f"Setting lighting to {request.params}")
        url = self.api.rpc.format(device_id=self.device_id)
        await self.http_client.request(url, payload=request.model_dump(), method="POST")

    async def test_rpc(self, request: Dict[str, Any]) -> RPCResponse:
        logger.info(f"Testing RPC")
        url = self._get_url_from_api(self.api.rpc)
        resp = await self.http_client.request(url, payload=request, method="POST", headers=self.headers)
        return RPCResponse(**resp)

    async def disconnect_device(self, device: Device) -> RPCResponse:
        logger.info(f"Disconnecting device {device.id}")
        url = self._get_url_from_api(self.api.rpc)
        payload = {
            "method": "disconnectDevice",
            "params": {
                "device_id": device.id
            }
        }
        resp = await self.http_client.request(url, payload=payload, method="POST", headers=self.headers)
        print(resp)
        return RPCResponse(**resp)
    # -------------------------------------------------------------
    # ----------------------------- Helper ------------------------
    # -------------------------------------------------------------

    async def _get_jwt(self):
        """Request for ThingsBoard JWT token"""
        payload = {
            "username": self.username,
            "password": self.password
        }
        try:
            response = await self.http_client.request(self.api.login_url, payload=payload, method="POST")
            if "token" not in response:
                raise Exception(f"Authentication response missing token field: {response}")

            return response["token"]
        except Exception as e:
            raise Exception(f"Connection error while authenticating: {str(e)}")

    def _get_url_from_api(self, api: str):
        return "https://" + self.broker_url + api.format(device_id=self.device_id)

    def _get_headers_with_jwt(self):
        return {
            "Authorization": f"Bearer {self._jwt}",
            "Content-Type": "application/json"
        }

import json
import asyncio
import websockets
from typing import Dict, Any, Tuple
from loguru import logger
from websockets.client import ClientConnection
import urllib.parse


from app.domain.events import EventBusInterface
from app.domain.repositories import MqttCloudClientRepository, HttpClientRepository
from app.domain.models import RPCResponse, DeviceUpdate, ActuatorUpdate, LightingSet, FanStateSet, COLOR_MAP


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

        self._jwt     = None
        self._rpc_api = None
        self._token_refresh_task = None
        self._token_refresh_interval = 600  # 10 minutes in seconds

    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    async def connect(self):
        self._jwt = await self._get_jwt()
        self._rpc_api = self._get_url_from_api(self.api.rpc.format(device_id=self.device_id))
        self.headers = self._get_headers_with_jwt()
        
        # Start token refresh task
        self._token_refresh_task = asyncio.create_task(self._token_refresh_loop())
        
        self._ws_listener_task = asyncio.create_task(self._thingsboard_ws_listener())
        logger.info(f"Thingsboard WS connected with token refresh every {self._token_refresh_interval/60} minutes!")

    async def disconnect(self):
        # Stop token refresh task
        if self._token_refresh_task and not self._token_refresh_task.done():
            self._token_refresh_task.cancel()
            try:
                await self._token_refresh_task
            except asyncio.CancelledError:
                pass
            
        if self._ws_listener_task and not self._ws_listener_task.done():
            self._ws_listener_task.cancel()
            try:
                await self._ws_listener_task
            except asyncio.CancelledError:
                pass
                
        logger.info(f"Thingsboard broker disconnected.")

    # -------------------------------------------------------------
    # ------------------------- Token Management ------------------
    # -------------------------------------------------------------

    async def _token_refresh_loop(self):
        """Background task to refresh JWT token every 10 minutes"""
        try:
            while True:
                await asyncio.sleep(self._token_refresh_interval)
                try:
                    logger.info("Refreshing ThingsBoard JWT token...")
                    old_jwt = self._jwt
                    self._jwt = await self._get_jwt()
                    self.headers = self._get_headers_with_jwt()
                    self._rpc_api = self._get_url_from_api(self.api.rpc.format(device_id=self.device_id))
                    logger.info("JWT token refreshed successfully")
                except Exception as e:
                    logger.error(f"Failed to refresh JWT token: {e}")
                    # Continue with old token, will retry in next cycle
        except asyncio.CancelledError:
            logger.info("Token refresh task cancelled")
        except Exception as e:
            logger.error(f"Token refresh loop error: {e}")

    async def refresh_token_now(self):
        """Manually refresh the token (useful for error recovery)"""
        try:
            logger.info("Manually refreshing ThingsBoard JWT token...")
            self._jwt = await self._get_jwt()
            self.headers = self._get_headers_with_jwt()
            self._rpc_api = self._get_url_from_api(self.api.rpc.format(device_id=self.device_id))
            logger.info("JWT token manually refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to manually refresh JWT token: {e}")
            return False

    # -------------------------------------------------------------
    # ------------------------- Listeners -------------------------
    # -------------------------------------------------------------

    async def _thingsboard_ws_listener(self):
        ws_url = self.api.ws_url + self._jwt
        try:
            async with websockets.connect(ws_url) as ws:
                logger.info(f"Thingsboard WS listener started!")
                try:
                    await self._ws_subscription_handle(ws)

                    async for message in ws:
                        try:
                            message_json = json.loads(message)
                            # logger.info(f"Parsed message: {message_json}")
                        except json.JSONDecodeError as e:
                            logger.error(f"Received non-JSON message: {message}, error: {e}")
                        except Exception as e:
                            logger.error(f"Error processing telemetry: {e}")
                except websockets.ConnectionClosed as e:
                    logger.error(f"Thingsboard WS session closed: {e.code} - {e}")
                    # If connection closed due to authentication, try refreshing token
                    if e.code in [1008, 4001, 4003]:  # Common auth error codes
                        logger.info("Attempting to refresh token due to auth error...")
                        if await self.refresh_token_now():
                            # Restart the WS connection with new token
                            logger.info("Token refreshed, restarting WS connection...")
                            # This will be handled by the main connection logic
                except Exception as e:
                    logger.error(f"Thingsboard WS connection error: {e}")
                finally:
                    logger.info("Thingsboard WS listener closed.")
        except Exception as e:
            logger.error(f"Failed to establish Thingsboard WS connection: {e}")

    # -------------------------------------------------------------
    # ----------------------------- RPC ---------------------------
    # -------------------------------------------------------------

    async def get_client_id(self, device_name: str) -> str:
        logger.info(f"Getting client ID for device {device_name}")
        encoded_name = urllib.parse.quote(device_name)
        url = self._get_url_from_api(self.api.get_client_id.format(device_name=encoded_name))
        
        try:
            resp = await self.http_client.request(url, method="GET", headers=self.headers)
            return resp["id"]["id"]
        except Exception as e:
            # If request fails due to auth, try refreshing token once
            if "401" in str(e) or "403" in str(e):
                logger.warning("Auth error detected, refreshing token...")
                if await self.refresh_token_now():
                    resp = await self.http_client.request(url, method="GET", headers=self.headers)
                    return resp["id"]["id"]
            raise

    async def send_rpc_command(self, request: Dict[str, Any]) -> RPCResponse:
        logger.info(f"Sending RPC command: {request}")
        url = self._rpc_api
        
        try:
            resp = await self.http_client.request(url, payload=request, method="POST", headers=self.headers)
            return RPCResponse(**resp)
        except Exception as e:
            # If request fails due to auth, try refreshing token once
            if "401" in str(e) or "403" in str(e):
                logger.warning("Auth error detected, refreshing token...")
                if await self.refresh_token_now():
                    resp = await self.http_client.request(url, payload=request, method="POST", headers=self.headers)
                    return RPCResponse(**resp)
            raise

    async def set_lighting(self, lighting_set: LightingSet) -> RPCResponse:
        logger.info(f"Setting lighting: {lighting_set}")
        url = self._rpc_api
        
        try:
            resp = await self.http_client.request(url, payload=lighting_set.model_dump(), method="POST", headers=self.headers)
            return RPCResponse(**resp)
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                logger.warning("Auth error detected, refreshing token...")
                if await self.refresh_token_now():
                    resp = await self.http_client.request(url, payload=lighting_set.model_dump(), method="POST", headers=self.headers)
                    return RPCResponse(**resp)
            raise

    async def set_fan_state(self, fan_state_set: FanStateSet) -> RPCResponse:
        logger.info(f"Setting fan state: {fan_state_set}")
        url = self._rpc_api
        
        try:
            resp = await self.http_client.request(url, payload=fan_state_set.model_dump(), method="POST", headers=self.headers)
            return RPCResponse(**resp)
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                logger.warning("Auth error detected, refreshing token...")
                if await self.refresh_token_now():
                    resp = await self.http_client.request(url, payload=fan_state_set.model_dump(), method="POST", headers=self.headers)
                    return RPCResponse(**resp)
            raise

    async def delete_device(self, device_id: int, cloud_device_id: str) -> RPCResponse:
        try:
            url = self._get_url_from_api(self.api.delete_device.format(device_id=cloud_device_id))
            resp = await self.http_client.request(url, method="DELETE", headers=self.headers)
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                logger.warning("Auth error detected, refreshing token...")
                if await self.refresh_token_now():
                    resp = await self.http_client.request(url, method="DELETE", headers=self.headers)
                else:
                    logger.error(f"Error deleting device: {e}")
                    return RPCResponse(status="error", data={"message": str(e)})
            else:
                logger.error(f"Error deleting device: {e}")
                return RPCResponse(status="error", data={"message": str(e)})

        logger.info(f"Deleting device {device_id}")
        url = self._rpc_api
        payload = {
            "method": "deleteDevice",
            "params": {
                "device_id": device_id
            }
        }
        
        try:
            resp = await self.http_client.request(url, payload=payload, method="POST", headers=self.headers)
            return RPCResponse(**resp)
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                logger.warning("Auth error detected, refreshing token...")
                if await self.refresh_token_now():
                    resp = await self.http_client.request(url, payload=payload, method="POST", headers=self.headers)
                    return RPCResponse(**resp)
            raise

    async def update_device(self, device_id: int, device_update: DeviceUpdate) -> RPCResponse:
        logger.info(f"Updating device {device_id} with {device_update}")
        url = self._rpc_api
        payload = {
            "method": "updateDevice",
            "params": {
                "device_id": device_id,
                "device_update": device_update.model_dump(exclude_unset=True)
            }
        }
        
        try:
            resp = await self.http_client.request(url, payload=payload, method="POST", headers=self.headers)
            return RPCResponse(**resp)
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                logger.warning("Auth error detected, refreshing token...")
                if await self.refresh_token_now():
                    resp = await self.http_client.request(url, payload=payload, method="POST", headers=self.headers)
                    return RPCResponse(**resp)
            raise

    async def update_actuator(self, actuator_id: int, actuator_update: ActuatorUpdate) -> RPCResponse:
        logger.info(f"Updating actuator {actuator_id} with {actuator_update}")
        url = self._rpc_api
        payload = {
            "method": "updateActuator",
            "params": {
                "actuator_id": actuator_id,
                "actuator_update": actuator_update.model_dump(exclude_unset=True)
            }
        }
        
        try:
            resp = await self.http_client.request(url, payload=payload, method="POST", headers=self.headers)
            print(f"Update actuator response: {resp}")
            return RPCResponse(**resp)
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                logger.warning("Auth error detected, refreshing token...")
                if await self.refresh_token_now():
                    resp = await self.http_client.request(url, payload=payload, method="POST", headers=self.headers)
                    print(f"Update actuator response: {resp}")
                    return RPCResponse(**resp)
            raise

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
        return "https://" + self.broker_url + api

    def _get_headers_with_jwt(self):
        return {
            "Authorization": f"Bearer {self._jwt}",
            "Content-Type": "application/json"
        }

    async def _ws_subscription_handle(self, ws: ClientConnection):
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

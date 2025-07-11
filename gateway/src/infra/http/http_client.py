from aiohttp import ClientSession, TCPConnector, ClientResponseError, ContentTypeError
from loguru import logger

from src.domain.repositories import HttpClientRepository
from src.domain.models import Device, DeviceCreate, DeviceStatus
from typing import Dict, List, Any


class HttpClient(HttpClientRepository):
    def __init__(self, url: str, api: Dict[str, str]):
        self.session = None
        self.url = url
        self.api = api

    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    async def connect(self):
        self.session = ClientSession(connector=TCPConnector(limit=10))
        logger.info(f"HTTP client initialized")

    async def disconnect(self):
        await self.session.close()
        logger.info(f"HTTP client disconnected")
    
    # -------------------------------------------------------------
    # ------------------------- Generic HTTP ----------------------
    # -------------------------------------------------------------

    async def get(self, endpoint: str, use_server_url: bool = False, expect_json: bool = True) -> Dict[str, Any] | None:
        """Generic GET method for sending data to any endpoint"""
        url = f"{self.url if use_server_url else ''}{endpoint}"
        try:
            response = await self._send_request(
                url=url,
                method="GET",
                expect_json=expect_json
            )
            return response
        except Exception as e:
            logger.error(f"Error in GET request to {endpoint}: {e}")
            return None

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any] | None:
        """Generic POST method for sending data to any endpoint"""
        url = f"{self.url}{endpoint}"
        try:
            response = await self._send_request(
                url=url,
                payload=data,
                method="POST"
            )
            return response
        except Exception as e:
            logger.error(f"Error in POST request to {endpoint}: {e}")
            return None

    # -------------------------------------------------------------
    # ------------------------- Device ----------------------------
    # -------------------------------------------------------------

    async def get_all_devices(self, return_components: bool = False) -> List[Device]:
        api = self.api['get_all_devices']
        url = f"{self.url}{api['url']}"
        response = await self._send_request(
            url=url,
            method=api['method'],
            params={'return_components': str(return_components).lower()}
            )
        return [Device(**device) for device in response]

    async def connect_device(self, device: Device) -> Device:
        api = self.api['connect_device']
        url = f"{self.url}{api['url']}"
        response = await self._send_request(
            url=url,
            payload=device.model_dump(exclude_none=True),
            method=api['method']
            )
        logger.info(f"Connected device: {response}")
        return Device(**response)

    async def create_device(self, device: DeviceCreate) -> Device:
        api = self.api['create_device']
        url = f"{self.url}{api['url']}"
        response = await self._send_request(
            url=url,
            payload=device.model_dump(exclude_none=True),
            method=api['method']
            )
        logger.info(f"Created device: {response}")
        return Device(**response)
    
    async def update_device(self, device_id: int, data: Dict[str, Any]) -> Device:
        api = self.api['update_device']
        url = f"{self.url}{api['url']}".format(device_id=device_id)
        response = await self._send_request(
            url=url,
            payload=data,
            method=api['method']
            )
        return Device(**response) if response else None
    
    async def delete_device(self, device_id: str) -> bool:
        api = self.api['delete_device']
        url = f"{self.url}{api['url']}".format(device_id=device_id)
        response = await self._send_request(
            url=url,
            payload=None,
            method=api['method']
            )
        return bool(response) if response else False
    
    async def set_device_status(self, device_id: str, status: DeviceStatus) -> bool:
        api = self.api['set_device_status']
        url = f"{self.url}{api['url']}".format(device_id=device_id)
        response = await self._send_request(
            url=url,
            payload={"status": status.value},
            method=api['method']
            )
        return bool(response) if response else False


    # -------------------------------------------------------------
    # ------------------------- Helper ----------------------------
    # -------------------------------------------------------------

    async def _send_request(
        self,
        url: str,
        payload: dict | None = None,
        method: str = "GET",
        headers: dict | None = None,
        params: dict | None = None,
        expect_json: bool = True
    ):
        if headers is None:
            headers = {}

        if expect_json:
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"
        else:
            headers.pop("Content-Type", None)
            headers["Accept"] = "image/jpeg"

        async with self.session.request(
            method,
            url,
            json=payload if expect_json else None,
            headers=headers,
            params=params
        ) as response:
            try:
                response.raise_for_status()
                if expect_json:
                    return await response.json()
                else:
                    return await response.read()
            except ContentTypeError:
                text = await response.text()
                raise Exception(f"HTTP response not JSON: {text}")
            except ClientResponseError as e:
                raise Exception(f"HTTP error {e.status}: {e.message}")

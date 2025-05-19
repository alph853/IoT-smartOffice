from aiohttp import ClientSession, TCPConnector, ClientResponseError, ContentTypeError
from loguru import logger

from src.domain.repositories import HttpClientRepository
from src.domain.models import Device, DeviceCreate
from typing import Dict, List


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
    # ------------------------- Device ----------------------------
    # -------------------------------------------------------------

    async def get_all_devices(self) -> List[Device]:
        api = self.api['get_all_devices']
        url = f"{self.url}{api['url']}"
        response = await self._send_request(
            url=url,
            method=api['method'],
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
    
    async def update_device(self, device: Device) -> Device:
        api = self.api['update_device']
        url = f"{self.url}{api['url']}"
        response = await self._send_request(
            url=url,
            payload=device.model_dump(exclude_none=True),
            method=api['method']
            )
        return Device(**response)
    
    async def delete_device(self, device_id: str) -> bool:
        api = self.api['delete_device']
        url = f"{self.url}{api['url']}"
        response = await self._send_request(
            url=url,
            payload=device_id,
            method=api['method']
            )
        return response
    # -------------------------------------------------------------
    # ------------------------- Helper ----------------------------
    # -------------------------------------------------------------

    async def _send_request(self, url: str, payload: dict | None = None, method: str = "GET",
                  headers: dict | None = None, params: dict | None = None):

        if headers is None:
            headers = {}
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        async with self.session.request(method, url, json=payload, headers=headers, params=params) as response:
            try:
                response.raise_for_status()
                return await response.json()
            except ContentTypeError:
                text = await response.text()
                raise Exception(f"HTTP response not JSON: {text}")
            except ClientResponseError as e:
                raise Exception(f"HTTP error {e.status}: {e.message}")
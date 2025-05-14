from aiohttp import ClientSession, TCPConnector
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

    async def disconnect(self):
        await self.session.close()

    # -------------------------------------------------------------
    # ------------------------- Device ----------------------------
    # -------------------------------------------------------------

    async def get_all_devices(self) -> List[Device]:
        url = f"{self.url}{self.api['get_all_devices']}"
        response = await self._send_request(
            url=url,
            method="GET",
            )
        logger.info(f"Received devices: {response}")
        return [Device(**device) for device in response]

    async def create_device(self, device: DeviceCreate) -> Device:
        response = await self._send_request(
            url=f"{self.url}{self.api['create_device']}",
            payload=device.model_dump(),
            method="POST"
            )
        logger.info(f"Created device: {response}")
        return Device(**response)
    
    async def update_device(self, device: Device) -> Device:
        response = await self._send_request(
            url=f"{self.url}{self.api['update_device']}",
            payload=device.model_dump(),
            method="PATCH"
            )
        return Device(**response)
    
    async def delete_device(self, device_id: str) -> bool:
        response = await self._send_request(
            url=f"{self.url}{self.api['delete_device']}",
            payload=device_id,
            method="DELETE"
            )
        return response
    # -------------------------------------------------------------
    # ------------------------- Helper ----------------------------
    # -------------------------------------------------------------

    async def _send_request(self, url: str, payload: dict | None = None, method: str = "GET", headers: dict | None = None):
        if headers is None:
            headers = {}
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
            
        async with self.session.request(method, url, json=payload, headers=headers) as response:
            return await response.json()
from aiohttp import ClientSession, TCPConnector

from src.domain.repositories import HttpClientRepository
from src.domain.models import Device
from typing import Dict, List


class HttpClient(HttpClientRepository):
    def __init__(self, url: str, api: Dict[str, str]):
        self.session = None
        self.url = url
        self.api = api

    async def connect(self):
        self.session = ClientSession(connector=TCPConnector(limit=10))

    async def disconnect(self):
        await self.session.close()

    async def get_all_devices(self) -> List[Device]:
        response = await self._send_request(
            url=f"{self.url}/{self.api['all_devices']}")
        return [Device(**device) for device in response]

    async def _send_request(self, url: str, payload: str | None = None, method: str = "GET", headers: dict | None = None):
        async with self.session.request(method, url, data=payload, headers=headers) as response:
            return await response.json()
    
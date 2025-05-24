from typing import Dict, Any
from aiohttp import ClientSession, ClientResponseError, ContentTypeError
import json

from app.domain.repositories import HttpClientRepository


class AiohttpClient(HttpClientRepository):
    def __init__(self):
        self.session = None

    async def connect(self):
        self.session = ClientSession()

    async def disconnect(self):
        await self.session.close()

    async def request(self, url: str, payload: dict | None = None, method: str = "GET",
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
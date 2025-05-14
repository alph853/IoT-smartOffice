from typing import Dict, Any
from app.domain.repositories import HttpClientRepository


class AiohttpClient(HttpClientRepository):
    async def connect(self):
        pass

    async def disconnect(self):
        pass


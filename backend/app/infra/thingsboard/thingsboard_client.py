import json
import asyncio
from typing import Dict, Any, Optional
import aiohttp
from app.domain.events import EventBusInterface
from app.domain.repositories import MqttCloudClientRepository


class ThingsBoardClient(MqttCloudClientRepository):
    def __init__(self, event_bus: EventBusInterface):
        self.event_bus = event_bus

    async def connect(self):
        pass

    async def disconnect(self):
        pass


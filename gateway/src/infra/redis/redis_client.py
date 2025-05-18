import redis.asyncio as redis
import asyncio
from typing import List
import json

from src.domain.models import Device
from src.domain.repositories import CacheClientRepository, HttpClientRepository
from loguru import logger


class RedisCacheClient(CacheClientRepository):
    def __init__(self, host: str, port: int, db: int, 
                 http_client: HttpClientRepository):
        self.host   = host
        self.port   = port
        self.db     = db
        self.client = None

        self.http_client = http_client

    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    async def connect(self):
        self.client = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
        await self.reset_cache()

        devices = await self.http_client.get_all_devices()
        await asyncio.gather(*[self.add_device(device) for device in devices])

        logger.info(f"Connected to Redis at {self.host}:{self.port} with database {self.db}")

    async def disconnect(self):
        await self.client.close()
        logger.info(f"Redis client disconnected")

    # -------------------------------------------------------------
    # ------------------------- Device ----------------------------
    # -------------------------------------------------------------

    async def get_all_devices(self) -> List[Device]:
        device_keys = await self.client.keys("device:id:*")
        devices = []
        for key in device_keys:
            device_data = await self.client.get(key)
            if device_data:
                devices.append(Device(**json.loads(device_data)))
        return devices
    
    async def get_device_by_id(self, device_id: str) -> Device | None:
        key = f"device:id:{device_id}"
        device_data = await self.client.get(key)
        if device_data:
            return Device(**json.loads(device_data))
        return None

    async def add_device(self, device: Device) -> Device:
        device_key    = f"device:id:{device.id}"
        await self.client.set(device_key, json.dumps(device.model_dump(exclude_none=True)))

        return device

    async def remove_device(self, device_id: str) -> bool:
        return await self.client.delete(f"device:id:{device_id}")

    async def update_device(self, device: Device) -> bool:
        pass

    # -------------------------------------------------------------
    # ------------------------- Control -------------------------
    # -------------------------------------------------------------

    async def get_control_device(self, device_id: str) -> Device | None:
        pass

    async def update_control_device(self, device_id: str, info: dict) -> bool:
        pass

    # -------------------------------------------------------------
    # ------------------------- Helper ----------------------------
    # -------------------------------------------------------------

    async def reset_cache(self):
        await self.client.flushdb()

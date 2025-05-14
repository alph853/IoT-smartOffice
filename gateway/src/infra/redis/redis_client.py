import redis.asyncio as redis
import asyncio
from typing import List
import json
from pydantic import BaseModel

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
        self.client = redis.Redis(host=self.host, port=self.port, db=self.db)
        await self.reset_cache()

        devices = await self.http_client.get_all_devices()
        tasks = [
            self.add_device(device) for device in devices
        ]
        await asyncio.gather(*tasks)
        logger.info(f"Connected to Redis at {self.host}:{self.port} with database {self.db}")
        val = await self.get_all_devices()
        logger.info(f"Devices: {val}")

    async def disconnect(self):
        await self.client.close()

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

    async def get_device_by_mac_addr(self, mac_addr: str) -> Device | None:
        device_id = await self.client.get(f"device:mac:{mac_addr}")
        if device_id:
            device = await self.get_device_by_id(device_id)
            return device
        return None
    
    async def get_device_by_id(self, device_id: str) -> Device | None:
        device_data = await self.client.get(f"device:id:{device_id}")
        if device_data:
            return Device(**json.loads(device_data))
        return None

    async def add_device(self, device: Device) -> Device:
        device_key    = f"device:id:{device.id}"
        mac_index_key = f"device:mac:{device.mac_addr}"

        await self.client.set(device_key, json.dumps(device.model_dump()))
        await self.client.set(mac_index_key, device.id)
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

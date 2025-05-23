import redis.asyncio as redis
import asyncio
from typing import List
import json

from src.domain.models import Device, DeviceStatus, DeviceMode
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

        devices = await self.http_client.get_all_devices(return_components=True)
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

    async def get_device_by_id(self, device_id: int) -> Device | None:
        key = f"device:id:{device_id}"
        device_data = await self.client.get(key)
        if device_data:
            return Device(**json.loads(device_data))
        return None

    async def add_device(self, device: Device) -> Device:
        device_key    = f"device:id:{device.id}"
        actuator_keys = {f"device:actuator:{actuator.id}" : device.id for actuator in device.actuators}
        sensor_keys   = {f"device:sensor:{sensor.id}" : device.id for sensor in device.sensors}

        async_tasks = [
            self.client.set(device_key, json.dumps(device.model_dump(exclude_none=True))),
            self.client.mset(actuator_keys),
            self.client.mset(sensor_keys)
        ]
        await asyncio.gather(*async_tasks)

        return device

    async def delete_device(self, device_id: int) -> bool:
        device = await self.get_device_by_id(device_id)
        if device:
            await self.client.delete(f"device:id:{device_id}")
            await self.client.delete(f"device:actuator:{actuator.id}" for actuator in device.actuators)
            await self.client.delete(f"device:sensor:{sensor.id}" for sensor in device.sensors)
            return True
        return False

    async def update_device(self, device_id: int, info: dict) -> bool:
        device_key  = f"device:id:{device_id}"
        device_data = await self.client.get(device_key)
        if device_data:
            device = json.loads(device_data)
            device.update(info)
            await self.client.set(device_key, json.dumps(device))
            return True
        return False

    async def get_status(self, device_id: int) -> DeviceStatus:
        device = await self.get_device_by_id(device_id)
        if device:
            return device.status
        return None

    async def get_mode(self, device_id: int) -> DeviceMode:
        device = await self.get_device_by_id(device_id)
        if device:
            return device.mode
        return None

    # -------------------------------------------------------------
    # ------------------------- Control -------------------------
    # -------------------------------------------------------------

    async def get_control_device(self, device_id: str) -> Device | None:
        pass

    async def update_control_device(self, device_id: str, info: dict) -> bool:
        pass

    async def get_device_id_by_actuator_id(self, actuator_id: int) -> int | None:
        device_key = f"device:actuator:{actuator_id}"
        device_id = await self.client.get(device_key)
        if device_id:
            return int(device_id)
        return None

    # -------------------------------------------------------------
    # ------------------------- Helper ----------------------------
    # -------------------------------------------------------------

    async def reset_cache(self):
        await self.client.flushdb()

from typing import List
from datetime import datetime
import asyncio
from loguru import logger

from app.domain.models import Device, DeviceRegistration, DeviceStatus, Sensor, Actuator, DeviceUpdate
from app.domain.repositories import DeviceRepository, MqttCloudClientRepository
from app.domain.events import EventBusInterface, DeviceConnectedEvent, DeviceDisconnectedEvent


class DeviceService:
    def __init__(self, event_bus: EventBusInterface,
                 device_repo: DeviceRepository,
                 cloud_client: MqttCloudClientRepository,
                 ):
        self.event_bus = event_bus
        self.device_repo = device_repo
        self.cloud_client = cloud_client

    async def start(self):
        logger.info("Device service started")

    async def stop(self):
        logger.info("Device service stopped")

    async def get_devices(self) -> List[Device]:
        return await self.device_repo.get_devices()

    async def get_device_by_id(self, device_id: int) -> Device:
        return await self.device_repo.get_device_by_id(device_id)

    async def connect_device(self, device_registration: DeviceRegistration) -> Device:
        """Create or update a device and connect it to the cloud"""
        device = await self.device_repo.get_device_by_mac_addr(device_registration.mac_addr)
        if device:
            device_update = DeviceUpdate(**device_registration.model_dump())
            device_update.status = DeviceStatus.ONLINE
            device_update.last_seen_at = datetime.now()
            device = await self.update_device(device.id, device_update)
        else:
            device = await self.create_device(device_registration)
        self.event_bus.publish(DeviceConnectedEvent(device=device))
        return device

    async def create_device(self, device_registration: DeviceRegistration) -> Device:
        """Only used for testing at server side. Device registration is done via MQTT client."""
        return await self.device_repo.create_device(device_registration)

    async def update_device(self, device_id: int, device_update: DeviceUpdate) -> Device | None:
        return await self.device_repo.update_device(device_id, device_update)

    async def delete_all_devices(self) -> bool:
        success = True
        all_devices = await self.device_repo.get_devices()
        if await self.device_repo.delete_all_devices():
            for device in all_devices:
                response = await self.cloud_client.delete_device(device.id)
                success = success and response.status == "success"
        return success

    async def delete_device(self, device_id: int) -> bool:
        device = await self.device_repo.get_device_by_id(device_id)
        if device:
            if await self.device_repo.delete_device(device_id):
                response = await self.cloud_client.delete_device(device_id)
                if response.status == "success":
                    await self.event_bus.publish(DeviceDisconnectedEvent(device=device))
                    return True
        return False

    async def disable_device(self, device_id: int) -> bool:
        updated_device = DeviceUpdate(status=DeviceStatus.DISABLED)
        device = await self.update_device(device_id, updated_device)
        if device:
            response = await self.cloud_client.update_device(device_id, updated_device)
            if response.status == "success":
                await self.event_bus.publish(DeviceDisconnectedEvent(device=device))
                return True
        return False

    async def enable_device(self, device_id: int) -> bool:
        updated_device = DeviceUpdate(status=DeviceStatus.ONLINE)
        device = await self.update_device(device_id, updated_device)
        if device:
            response = await self.cloud_client.update_device(device_id, updated_device)
            if response.status == "success":
                await self.event_bus.publish(DeviceConnectedEvent(device=device))
                return True
        return False

    async def get_all_sensors(self) -> List[Sensor]:
        return await self.device_repo.get_all_sensors()

    async def get_all_actuators(self) -> List[Actuator]:
        return await self.device_repo.get_all_actuators()


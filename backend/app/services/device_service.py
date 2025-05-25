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

    async def get_devices(self, return_components: bool = False) -> List[Device]:
        devices = await self.device_repo.get_devices()
        if return_components:
            for device in devices:
                device.sensors = await self.device_repo.get_sensors_by_device_id(device.id)
                device.actuators = await self.device_repo.get_actuators_by_device_id(device.id)
        return devices

    async def get_device_by_id(self, device_id: int, return_components: bool = False) -> Device:
        device = await self.device_repo.get_device_by_id(device_id)
        if device and return_components:
            device.sensors = await self.device_repo.get_sensors_by_device_id(device.id)
            device.actuators = await self.device_repo.get_actuators_by_device_id(device.id)
        return device

    async def connect_device(self, device_registration: DeviceRegistration, return_components: bool = True) -> Device:
        """Create or update a device and connect it to the cloud"""
        device = await self.device_repo.get_device_by_mac_addr(device_registration.mac_addr)
        if device:
            device_update = DeviceUpdate(**device_registration.model_dump())
            device_update.status = DeviceStatus.ONLINE
            device_update.last_seen_at = datetime.now()
            device = await self.update_device(device.id, device_update, return_components)
        else:
            device = await self.create_device(device_registration, return_components)

        await self.event_bus.publish(DeviceConnectedEvent(device=device))
        return device

    async def create_device(self, device_registration: DeviceRegistration, return_components: bool = False) -> Device:
        """Only used for testing at server side. Device registration is done via MQTT client."""
        device_registration.device_id = await self.cloud_client.get_client_id(device_registration.name)
        device = await self.device_repo.create_device(device_registration)
        if return_components:
            device.sensors = await self.device_repo.get_sensors_by_device_id(device.id)
            device.actuators = await self.device_repo.get_actuators_by_device_id(device.id)
        return device

    async def update_device(self, device_id: int, device_update: DeviceUpdate, return_components: bool = False) -> Device | None:
        device = await self.device_repo.update_device(device_id, device_update)
        if device and return_components:
            device.sensors = await self.device_repo.get_sensors_by_device_id(device.id)
            device.actuators = await self.device_repo.get_actuators_by_device_id(device.id)
        if device:
            device.id = device_id
        return device

    async def delete_all_devices(self) -> bool:
        try:
            all_devices = await self.device_repo.get_devices()
            if await self.device_repo.delete_all_devices():
                for device in all_devices:
                    asyncio.create_task(self._cleanup_cloud_device(device))
            return True
        except Exception as e:
            logger.error(f"Error deleting all devices: {e}")
            return False

    async def delete_device(self, device_id: int) -> bool:
        try:
            device = await self.device_repo.get_device_by_id(device_id)
            if device:
                if await self.device_repo.delete_device(device_id):
                    asyncio.create_task(self._cleanup_cloud_device(device))
                return True
        except Exception as e:
            logger.error(f"Error deleting device {device_id}: {e}")
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

    async def _cleanup_cloud_device(self, device: Device):
        try:
            response = await self.cloud_client.delete_device(device.id, device.device_id)
            if response.status == "success":
                await self.event_bus.publish(DeviceDisconnectedEvent(device=device))
        except Exception as e:
            logger.error(f"Error cleaning up device {device.id} from cloud: {e}")

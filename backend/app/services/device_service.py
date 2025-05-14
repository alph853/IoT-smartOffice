from typing import List
import logging
from datetime import datetime
import asyncio

from app.domain.models import Device, DeviceRegistration, DeviceMode, DeviceStatus, Sensor, Actuator
from app.domain.repositories import DeviceRepository


logger = logging.getLogger(__name__)


class DeviceService:
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository

    def start(self):
        logger.info("Device service started")

    def stop(self):
        logger.info("Device service stopped")

    async def get_devices(self) -> List[Device]:
        return await self.device_repository.get_devices()

    async def get_device_by_id(self, device_id: str) -> Device:
        return await self.device_repository.get_device_by_id(device_id)

    async def create_device(self, device_registration: DeviceRegistration) -> Device:
        device = Device(
            name=device_registration.name,
            mode=DeviceMode.MANUAL,
            registered_at=datetime.now(),
            mac_addr=device_registration.mac_addr,
            description=device_registration.description,
            fw_version=device_registration.fw_version,
            last_seen_at=datetime.now(),
            model=device_registration.model,
            office_id=device_registration.office_id,
            gateway_id=device_registration.gateway_id,
            status=DeviceStatus.ONLINE,
            access_token=None,
        )
        device = await self.device_repository.create_device(device)

        for sensor in device_registration.sensors:
            sensor.device_id = device.id
        for actuator in device_registration.actuators:
            actuator.device_id = device.id

        create_tasks = [
            self.device_repository.create_sensor(sensor)
            for sensor in device_registration.sensors
        ] + [
            self.device_repository.create_actuator(actuator)
            for actuator in device_registration.actuators
        ]
        await asyncio.gather(*create_tasks)
        return device

    async def update_device(self, device_id: str, device: Device) -> Device:
        return await self.device_repository.update_device(device_id, device)

    async def delete_device(self, device_id: str) -> Device:
        return await self.device_repository.delete_device(device_id)


from typing import List

from app.domain.models import Device, Sensor, Actuator, SensorReading, DeviceMode, DeviceStatus
from app.domain.repositories import DeviceRepository
from app.infra.postgres.db import PostgreSQLConnection
from app.infra.postgres.scripts.sql_device import *


class PostgresDeviceRepository(DeviceRepository):
    def __init__(self, db: PostgreSQLConnection):
        self.db = db

    async def get_devices(self) -> List[Device]:
        async with self.db.acquire() as conn:
            query = GET_ALL_DEVICES
            result = await conn.fetch(query)
            return [Device(**row) for row in result]

    async def get_device_by_id(self, device_id: str) -> Device:
        async with self.db.acquire() as conn:
            query = GET_DEVICE_BY_ID
            result = await conn.fetch(query, (device_id,))
            return Device(**result)

    async def create_device(self, device: Device) -> Device:
        async with self.db.acquire() as conn:
            query = CREATE_DEVICE
            record = await conn.fetch(query,
                                      device.name,
                                      device.mode.value,
                                      device.registered_at,
                                      device.mac_addr,
                                      device.description,
                                      device.fw_version,
                                      device.last_seen_at,
                                      device.model,
                                      device.office_id,
                                      device.gateway_id,
                                      device.status.value,
                                      device.access_token
                                     )
            return Device(**record[0])

    async def update_device(self, device: Device) -> Device:
        pass

    async def delete_device(self, id: int) -> None:
        raise NotImplementedError("Not implemented")


    async def get_all_sensors(self) -> List[Sensor]:
        pass

    async def get_sensor(self, id: int) -> Sensor:
        pass

    async def get_all_actuators(self) -> List[Actuator]:
        pass

    async def get_actuator(self, id: int) -> Actuator:
        pass

    async def create_sensor(self, sensor: Sensor) -> Sensor:
        async with self.db.acquire() as conn:
            query = CREATE_SENSOR
            result = await conn.fetch(query, sensor.name, sensor.type, sensor.unit, sensor.device_id)
            return Sensor(**result[0])

    async def create_actuator(self, actuator: Actuator) -> Actuator:
        async with self.db.acquire() as conn:
            query = CREATE_ACTUATOR
            result = await conn.fetch(query, actuator.name, actuator.type, actuator.device_id)
            return Actuator(**result[0])

    async def create_sensor_reading(self, sensor_reading: SensorReading) -> SensorReading:
        pass

    async def get_all_sensor_readings(self) -> List[SensorReading]:
        pass

    async def get_sensor_reading(self, id: int) -> SensorReading:
        pass

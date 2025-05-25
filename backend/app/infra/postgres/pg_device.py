from typing import List
import re
import enum
from loguru import logger
import json

from app.domain.models import Device, Sensor, Actuator, SensorReading, DeviceUpdate, DeviceRegistration, SensorUpdate, ActuatorUpdate, LightingSetParams, FanStateSetParams, DeviceMode
from app.domain.repositories import DeviceRepository
from app.infra.postgres.db import PostgreSQLConnection
from app.infra.postgres.scripts.sql_device import *
from app.domain.models import LightingSetParams


class PostgresDeviceRepository(DeviceRepository):
    def __init__(self, db: PostgreSQLConnection):
        self.db = db

    async def get_devices(self) -> List[Device]:
        async with self.db.acquire() as conn:
            query = GET_ALL_DEVICES
            result = await conn.fetch(query)
            return [Device(**row) for row in result]

    async def get_device_by_id(self, device_id: int) -> Device:
        async with self.db.acquire() as conn:
            query = GET_DEVICE_BY_ID
            result = await conn.fetch(query, device_id)
            return Device(**result[0]) if result else None

    async def get_device_by_mac_addr(self, mac_addr: str) -> Device:
        async with self.db.acquire() as conn:
            query = GET_DEVICE_BY_MAC_ADDR
            result = await conn.fetch(query, mac_addr)
            return Device(**result[0]) if result else None

    async def create_device(self, device_registration: DeviceRegistration) -> Device:
        """Create a device. The thingsboard name is the first name it gets."""
        async with self.db.acquire() as conn:
            async with conn.transaction():
                device = Device(**device_registration.model_dump())
                query = CREATE_DEVICE
                device_name = await self._get_unique_device_name(device.name)
                device_record = await conn.fetch(query,
                                          device_name,
                                          device.registered_at,
                                          device.mac_addr,
                                          device.description,
                                          device.fw_version,
                                          device.last_seen_at,
                                          device.model,
                                          device.office_id,
                                          device.gateway_id,
                                          device.status.value,
                                          device.access_token,
                                          device.name,
                                          device.device_id
                                          )
                device = Device(**device_record[0])

                for sensor in device_registration.sensors:
                    sensor.device_id = device.id
                    await self.create_sensor(sensor, conn)
                for actuator in device_registration.actuators:
                    actuator.device_id = device.id
                    await self.create_actuator(actuator, conn)

                return device

    async def create_sensor(self, sensor: Sensor, conn=None) -> Sensor:
        query = CREATE_SENSOR
        params = [sensor.name, sensor.type, sensor.unit, sensor.device_id]
        if conn is None:
            async with self.db.acquire() as conn:
                result = await conn.fetch(query, *params)
        else:
            result = await conn.fetch(query, *params)
        return Sensor(**result[0])

    async def create_actuator(self, actuator: Actuator, conn=None) -> Actuator:
        if actuator.type == "led4RGB":
            actuator.setting = {"color": ((0,0,0), (0,0,0), (0,0,0), (0,0,0))}
        elif actuator.type == "fan":
            actuator.setting = {"state": False}
        query = CREATE_ACTUATOR
        params = [actuator.name, actuator.type, actuator.device_id, actuator.mode.value if isinstance(actuator.mode, enum.Enum) else actuator.mode, json.dumps(actuator.setting)]
        if conn is None:
            async with self.db.acquire() as conn:
                result = await conn.fetch(query, *params)
        else:
            result = await conn.fetch(query, *params)
        return Actuator(
            id=result[0]["id"],
            name=result[0]["name"],
            type=result[0]["type"],
            device_id=result[0]["device_id"],
            mode=result[0]["mode"],
            setting=json.loads(result[0]["setting"])
        )
    async def update_device(self, device_id: int, device_update: DeviceUpdate) -> Device | None:
        async with self.db.acquire() as conn:
            if device_update.name is not None:
                device_update.name = await self._get_unique_device_name(device_update.name)
            update_fields = device_update.model_dump(exclude_unset=True)

            if not update_fields:
                return None

            set_clauses = []
            values = []

            for idx, (field, value) in enumerate(update_fields.items()):
                if field in ("sensors", "actuators"):
                    continue
                set_clauses.append(f"{field} = ${idx + 2}")
                if isinstance(value, enum.Enum):
                    value = value.value
                values.append(value)

            query = UPDATE_DEVICE.format(set_clauses=', '.join(set_clauses))
            result = await conn.fetch(query, device_id, *values)

            if device_update.actuators is not None:
                if await self.delete_actuators_by_device_id(device_id, conn):
                    for actuator in device_update.actuators:
                        actuator.device_id = device_id
                        await self.create_actuator(actuator, conn)
                else:
                    logger.error(f"Failed to delete actuators for device {device_id}")
            if device_update.sensors is not None:
                if await self.delete_sensors_by_device_id(device_id, conn):
                    for sensor in device_update.sensors:
                        sensor.device_id = device_id
                        await self.create_sensor(sensor, conn)
                else:
                    logger.error(f"Failed to delete sensors for device {device_id}")

            return Device(**result[0]) if result else None

    async def delete_all_devices(self) -> bool:
        async with self.db.acquire() as conn:
            query = DELETE_ALL_DEVICES
            result = await conn.execute(query)
            return bool(result[-1])

    async def delete_device(self, device_id: str) -> bool:
        async with self.db.acquire() as conn:
            query = DELETE_DEVICE
            result = await conn.execute(query, device_id)
            return bool(result[-1])

    async def get_all_sensors(self) -> List[Sensor]:
        async with self.db.acquire() as conn:
            query = GET_ALL_SENSORS
            result = await conn.fetch(query)
            return [Sensor(**row) for row in result]

    async def get_sensor(self, id: int) -> Sensor | None:
        async with self.db.acquire() as conn:
            query = GET_SENSOR_BY_ID
            result = await conn.fetch(query, id)
            return Sensor(**result[0]) if result else None

    async def update_sensor(self, id: int, sensor_update: SensorUpdate) -> Sensor | None:
        async with self.db.acquire() as conn:
            update_fields = sensor_update.model_dump(exclude_unset=True)
            if not update_fields:
                return None
            set_clauses = []
            values = []
            for idx, (field, value) in enumerate(update_fields.items()):
                set_clauses.append(f"{field} = ${idx + 2}")
                values.append(value)

            query = UPDATE_SENSOR.format(set_clauses=', '.join(set_clauses))
            result = await conn.fetch(query, id, *values)
            return Sensor(**result[0]) if result else None

    async def delete_sensors_by_device_id(self, device_id: int, conn=None) -> bool:
        query = DELETE_SENSORS_BY_DEVICE_ID
        if conn is None:
            async with self.db.acquire() as conn:
                result = await conn.execute(query, device_id)
        else:
            result = await conn.execute(query, device_id)
        return bool(result[-1])

    async def get_all_actuators(self) -> List[Actuator]:
        async with self.db.acquire() as conn:
            query = GET_ALL_ACTUATORS
            result = await conn.fetch(query)
            return [Actuator(id=row["id"],
                             name=row["name"],
                             type=row["type"],
                             device_id=row["device_id"],
                             mode=row["mode"],
                             setting=json.loads(row["setting"]) if row["setting"] else None)
                    for row in result]

    async def get_actuator(self, id: int, conn=None) -> Actuator | None:
        query = GET_ACTUATOR_BY_ID
        if conn is None:
            async with self.db.acquire() as conn:
                result = await conn.fetch(query, id)
        else:
            result = await conn.fetch(query, id)
        if not result:
            return None
        return Actuator(id=result[0]["id"],
                        name=result[0]["name"],
                        type=result[0]["type"],
                        device_id=result[0]["device_id"],
                        mode=result[0]["mode"],
                        setting=json.loads(result[0]["setting"]) if result[0]["setting"] else None)

    async def update_actuator(self, id: int, actuator_update: ActuatorUpdate) -> Actuator | None:
        async with self.db.acquire() as conn:
            if actuator_update.setting is not None:
                actuator = await self.get_actuator(id, conn)
                if actuator.mode == DeviceMode.AUTO.value:
                    return None
                actuator_update.setting = json.dumps(actuator_update.setting)
            update_fields = actuator_update.model_dump(exclude_unset=True)
            if not update_fields:
                return None
            set_clauses = []
            values = []
            for idx, (field, value) in enumerate(update_fields.items()):
                set_clauses.append(f"{field} = ${idx + 2}")
                values.append(value)

            query = UPDATE_ACTUATOR.format(set_clauses=', '.join(set_clauses))
            result = await conn.fetch(query, id, *values)
            return Actuator(id=result[0]["id"],
                            name=result[0]["name"],
                            type=result[0]["type"],
                            device_id=result[0]["device_id"],
                            mode=result[0]["mode"],
                            setting=json.loads(result[0]["setting"]) if result[0]["setting"] else None) if result else None

    async def delete_actuators_by_device_id(self, device_id: int, conn=None) -> bool:
        query = DELETE_ACTUATORS_BY_DEVICE_ID
        if conn is None:
            async with self.db.acquire() as conn:
                result = await conn.execute(query, device_id)
        else:
            result = await conn.execute(query, device_id)
        return bool(result[-1])

    async def create_sensor_reading(self, sensor_reading: SensorReading) -> SensorReading:
        pass

    async def get_all_sensor_readings(self) -> List[SensorReading]:
        pass

    async def get_sensor_reading(self, id: int) -> SensorReading:
        pass

    async def get_sensors_by_device_id(self, device_id: int) -> List[Sensor]:
        async with self.db.acquire() as conn:
            query = GET_SENSORS_BY_DEVICE_ID
            result = await conn.fetch(query, device_id)
            return [Sensor(**row) for row in result]

    async def get_actuators_by_device_id(self, device_id: int) -> List[Actuator]:
        async with self.db.acquire() as conn:
            query = GET_ACTUATORS_BY_DEVICE_ID
            result = await conn.fetch(query, device_id)
            return [Actuator(
                id=row['id'],
                name=row['name'],
                type=row['type'],
                device_id=row['device_id'],
                mode=row['mode'],
                setting=json.loads(row['setting']) if row['setting'] else None
            ) for row in result]

    # -----------------------------------------------------------------------
    # ------------------------------ Helpers --------------------------------
    # -----------------------------------------------------------------------

    async def _get_unique_device_name(self, base_name: str) -> str:
        async with self.db.acquire() as conn:
            rows = await conn.fetch(
                "SELECT name FROM device WHERE name ~ $1", f"^{re.escape(base_name)}( \\([0-9]+\\))?$"
            )
        existing = [r['name'] for r in rows]

        if base_name not in existing:
            return base_name

        suffixes = [
            int(re.search(r'\((\d+)\)$', name).group(1))
            for name in existing
            if re.search(r'\((\d+)\)$', name)
        ]
        next_suffix = max(suffixes, default=0) + 1
        return f"{base_name} ({next_suffix})"

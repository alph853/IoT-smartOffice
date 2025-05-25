from typing import List, Optional
from loguru import logger

from app.domain.models import Device, Sensor, Actuator, SensorReading
from app.domain.repositories import DeviceRepository


class MockDeviceRepository(DeviceRepository):
    def __init__(self):
        self.devices: List[Device] = []
        self.sensors: List[Sensor] = []
        self.actuators: List[Actuator] = []
        self.sensor_readings: List[SensorReading] = []

    async def get_devices(self) -> List[Device]:
        logger.info("Mock: Getting all devices")
        return self.devices

    async def get_device_by_id(self, device_id: str) -> Optional[Device]:
        logger.info(f"Mock: Getting device by ID {device_id}")
        return next((d for d in self.devices if d.id == device_id), None)

    async def get_device_by_mac_addr(self, mac_addr: str) -> Optional[Device]:
        logger.info(f"Mock: Getting device by MAC address {mac_addr}")
        return next((d for d in self.devices if d.mac_addr == mac_addr), None)

    async def create_device(self, device: Device) -> Device:
        logger.info(f"Mock: Creating device {device}")
        self.devices.append(device)
        return device

    async def update_device(self, device_id: str, device: Device) -> Device:
        logger.info(f"Mock: Updating device {device_id}")
        for i, d in enumerate(self.devices):
            if d.id == device_id:
                self.devices[i] = device
                return device
        return device

    async def delete_all_devices(self) -> bool:
        logger.info("Mock: Deleting all devices")
        self.devices.clear()
        return True

    async def delete_device(self, device_id: str) -> bool:
        logger.info(f"Mock: Deleting device {device_id}")
        self.devices = [d for d in self.devices if d.id != device_id]
        return True

    async def get_all_sensors(self) -> List[Sensor]:
        logger.info("Mock: Getting all sensors")
        return self.sensors

    async def get_sensor(self, id: int) -> Sensor:
        logger.info(f"Mock: Getting sensor {id}")
        return next((s for s in self.sensors if s.id == id), None)

    async def create_sensor(self, sensor: Sensor) -> Sensor:
        logger.info(f"Mock: Creating sensor {sensor}")
        self.sensors.append(sensor)
        return sensor

    async def get_all_actuators(self) -> List[Actuator]:
        logger.info("Mock: Getting all actuators")
        return self.actuators

    async def get_actuator(self, id: int) -> Actuator:
        logger.info(f"Mock: Getting actuator {id}")
        return next((a for a in self.actuators if a.id == id), None)

    async def update_actuator(self, actuator_id: int, actuator: Actuator) -> Actuator:
        logger.info(f"Mock: Updating actuator {actuator_id}")
        for i, a in enumerate(self.actuators):
            if a.id == actuator_id:
                self.actuators[i] = actuator
                return actuator
        return actuator

    async def create_actuator(self, actuator: Actuator) -> Actuator:
        logger.info(f"Mock: Creating actuator {actuator}")
        self.actuators.append(actuator)
        return actuator

    async def create_sensor_reading(self, sensor_reading: SensorReading) -> SensorReading:
        logger.info(f"Mock: Creating sensor reading {sensor_reading}")
        self.sensor_readings.append(sensor_reading)
        return sensor_reading

    async def get_sensors_by_device_id(self, device_id: int) -> List[Sensor]:
        logger.info(f"Mock: Getting sensors for device {device_id}")
        return [s for s in self.sensors if s.device_id == device_id]

    async def get_actuators_by_device_id(self, device_id: int) -> List[Actuator]:
        logger.info(f"Mock: Getting actuators for device {device_id}")
        return [a for a in self.actuators if a.device_id == device_id]

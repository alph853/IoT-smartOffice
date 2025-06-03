from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Device, Sensor, Actuator


class DeviceRepository(ABC):
    @abstractmethod
    async def get_devices(self) -> List[Device]:
        pass

    @abstractmethod
    async def get_device_by_id(self, device_id: str) -> Optional[Device]:
        pass

    @abstractmethod
    async def get_device_by_mac_addr(self, mac_addr: str) -> Optional[Device]:
        pass

    @abstractmethod
    async def create_device(self, device: Device) -> Device:
        pass

    @abstractmethod
    async def update_device(self, device_id: str, device: Device) -> Device:
        pass

    @abstractmethod
    async def delete_all_devices(self) -> bool:
        pass

    @abstractmethod
    async def delete_device(self, device_id: str) -> bool:
        pass

    @abstractmethod
    async def get_all_sensors(self) -> List[Sensor]:
        pass

    @abstractmethod
    async def get_sensor(self, id: int) -> Sensor:
        pass

    @abstractmethod
    async def create_sensor(self, sensor: Sensor) -> Sensor:
        pass

    @abstractmethod
    async def get_all_actuators(self) -> List[Actuator]:
        pass

    @abstractmethod
    async def get_actuator(self, id: int) -> Actuator:
        pass

    @abstractmethod
    async def update_actuator(self, actuator_id: int, actuator: Actuator) -> Actuator:
        pass

    @abstractmethod
    async def create_actuator(self, actuator: Actuator) -> Actuator:
        pass

    @abstractmethod
    async def get_sensors_by_device_id(self, device_id: int) -> List[Sensor]:
        pass

    @abstractmethod
    async def get_actuators_by_device_id(self, device_id: int) -> List[Actuator]:
        pass

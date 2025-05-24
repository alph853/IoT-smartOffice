from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.domain.models import SensorReading


class SensorRepository(ABC):
    @abstractmethod
    async def save_sensor_reading(self, reading: SensorReading) -> None:
        pass

    @abstractmethod
    async def get_sensor_readings(self, device_id: str, start_time: datetime, end_time: datetime) -> List[SensorReading]:
        pass

    @abstractmethod
    async def get_latest_sensor_reading(self, device_id: str) -> Optional[SensorReading]:
        pass

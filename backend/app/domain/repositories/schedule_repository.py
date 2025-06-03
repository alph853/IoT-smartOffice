from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import Schedule, ScheduleCreate, ScheduleUpdate


class ScheduleRepository(ABC):
    @abstractmethod
    async def get_all_schedules(self) -> List[Schedule]:
        pass

    @abstractmethod
    async def get_schedule_by_id(self, schedule_id: str) -> Optional[Schedule]:
        pass

    @abstractmethod
    async def get_schedules_by_actuator_id(self, actuator_id: int) -> List[Schedule]:
        pass

    @abstractmethod
    async def create_schedule(self, schedule: ScheduleCreate) -> Schedule:
        pass

    @abstractmethod
    async def update_schedule(self, schedule_id: str, schedule_update: ScheduleUpdate) -> Optional[Schedule]:
        pass

    @abstractmethod
    async def delete_schedule(self, schedule_id: str) -> bool:
        pass

    @abstractmethod
    async def get_active_schedules(self) -> List[Schedule]:
        pass

    @abstractmethod
    async def get_schedules_by_type(self, schedule_type: str) -> List[Schedule]:
        pass 
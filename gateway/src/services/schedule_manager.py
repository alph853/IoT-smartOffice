from datetime import time
from typing import List, Optional
from uuid import uuid4
import asyncio

from src.services.scheduler_service import (
    SchedulerService, 
    Schedule, 
    DayOfWeek, 
    ScheduleType,
    LightingScheduleSetting,
    FanScheduleSetting
)
from loguru import logger


class ScheduleManager:
    """High-level manager for creating and managing device schedules"""
    
    def __init__(self, scheduler_service: SchedulerService):
        self.scheduler_service = scheduler_service

    async def create_lighting_schedule(
        self,
        name: str,
        actuator_id: int,
        days_of_week: List[DayOfWeek],
        start_time: time,
        end_time: time,
        color: tuple[tuple[int, int, int], ...],
        brightness: int = 100,
        priority: int = 0
    ) -> str:
        """Create a lighting schedule and return its ID"""
        schedule_id = str(uuid4())
        
        setting = {
            "color": color,
            "brightness": brightness
        }
        
        schedule = Schedule(
            id=schedule_id,
            name=name,
            actuator_id=actuator_id,
            schedule_type=ScheduleType.LIGHTING,
            days_of_week=days_of_week,
            start_time=start_time,
            end_time=end_time,
            setting=setting,
            priority=priority
        )
        
        await self.scheduler_service.add_schedule(schedule)
        logger.info(f"Created lighting schedule '{name}' with ID {schedule_id}")
        return schedule_id

    async def create_fan_schedule(
        self,
        name: str,
        actuator_id: int,
        days_of_week: List[DayOfWeek],
        start_time: time,
        end_time: time,
        state: bool,
        speed: Optional[int] = None,
        priority: int = 0
    ) -> str:
        """Create a fan schedule and return its ID"""
        schedule_id = str(uuid4())
        
        setting = {
            "state": state,
            "speed": speed
        }
        
        schedule = Schedule(
            id=schedule_id,
            name=name,
            actuator_id=actuator_id,
            schedule_type=ScheduleType.FAN,
            days_of_week=days_of_week,
            start_time=start_time,
            end_time=end_time,
            setting=setting,
            priority=priority
        )
        
        await self.scheduler_service.add_schedule(schedule)
        logger.info(f"Created fan schedule '{name}' with ID {schedule_id}")
        return schedule_id

    async def create_workday_lighting_schedule(
        self,
        name: str,
        actuator_id: int,
        start_hour: int,
        start_minute: int,
        end_hour: int,
        end_minute: int,
        color: tuple[tuple[int, int, int], ...],
        brightness: int = 100,
        priority: int = 0
    ) -> str:
        """Create a lighting schedule for weekdays (Monday-Friday)"""
        workdays = [
            DayOfWeek.MONDAY,
            DayOfWeek.TUESDAY,
            DayOfWeek.WEDNESDAY,
            DayOfWeek.THURSDAY,
            DayOfWeek.FRIDAY
        ]
        
        return await self.create_lighting_schedule(
            name=name,
            actuator_id=actuator_id,
            days_of_week=workdays,
            start_time=time(start_hour, start_minute),
            end_time=time(end_hour, end_minute),
            color=color,
            brightness=brightness,
            priority=priority
        )

    async def create_weekend_lighting_schedule(
        self,
        name: str,
        actuator_id: int,
        start_hour: int,
        start_minute: int,
        end_hour: int,
        end_minute: int,
        color: tuple[tuple[int, int, int], ...],
        brightness: int = 100,
        priority: int = 0
    ) -> str:
        """Create a lighting schedule for weekends (Saturday-Sunday)"""
        weekends = [DayOfWeek.SATURDAY, DayOfWeek.SUNDAY]
        
        return await self.create_lighting_schedule(
            name=name,
            actuator_id=actuator_id,
            days_of_week=weekends,
            start_time=time(start_hour, start_minute),
            end_time=time(end_hour, end_minute),
            color=color,
            brightness=brightness,
            priority=priority
        )

    async def remove_schedule(self, schedule_id: str) -> bool:
        """Remove a schedule"""
        return await self.scheduler_service.remove_schedule(schedule_id)

    async def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Get a specific schedule"""
        return await self.scheduler_service.get_schedule(schedule_id)

    async def get_schedules_for_actuator(self, actuator_id: int) -> List[Schedule]:
        """Get all schedules for an actuator"""
        return await self.scheduler_service.get_schedules_for_actuator(actuator_id)

    async def get_all_schedules(self) -> List[Schedule]:
        """Get all schedules"""
        return await self.scheduler_service.get_all_schedules()

    async def create_example_schedules(self, led_actuator_id: int, fan_actuator_id: int):
        """Create some example schedules for demonstration"""
        
        # Office hours lighting - bright white
        await self.create_workday_lighting_schedule(
            name="Office Hours - Bright White",
            actuator_id=led_actuator_id,
            start_hour=9,
            start_minute=0,
            end_hour=17,
            end_minute=0,
            color=((255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255)),
            brightness=100,
            priority=1
        )
        
        # Evening mood lighting - warm yellow
        await self.create_lighting_schedule(
            name="Evening Mood - Warm Yellow",
            actuator_id=led_actuator_id,
            days_of_week=[DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY, 
                         DayOfWeek.THURSDAY, DayOfWeek.FRIDAY],
            start_time=time(17, 30),
            end_time=time(22, 0),
            color=((255, 200, 100), (255, 200, 100), (255, 200, 100), (255, 200, 100)),
            brightness=70,
            priority=2
        )
        
        # Weekend relaxing lighting - soft blue
        await self.create_weekend_lighting_schedule(
            name="Weekend Relaxing - Soft Blue",
            actuator_id=led_actuator_id,
            start_hour=10,
            start_minute=0,
            end_hour=20,
            end_minute=0,
            color=((100, 150, 255), (100, 150, 255), (100, 150, 255), (100, 150, 255)),
            brightness=60,
            priority=1
        )
        
        # Office hours fan - on during work hours
        await self.create_workday_lighting_schedule(
            name="Office Hours Fan",
            actuator_id=fan_actuator_id,
            start_hour=9,
            start_minute=0,
            end_hour=17,
            end_minute=0,
            color=((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)),  # Dummy for compatibility
            brightness=100,
            priority=1
        )
        
        # Actually create fan schedule (overwrite the lighting one above)
        await self.create_fan_schedule(
            name="Office Hours Fan",
            actuator_id=fan_actuator_id,
            days_of_week=[DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY, 
                         DayOfWeek.THURSDAY, DayOfWeek.FRIDAY],
            start_time=time(9, 0),
            end_time=time(17, 0),
            state=True,
            speed=75,
            priority=1
        )
        
        logger.info("Example schedules created successfully") 
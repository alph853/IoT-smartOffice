import asyncio
from datetime import datetime, time
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from loguru import logger

from src.domain.repositories import CacheClientRepository
from src.domain.events import EventBusInterface, SetLightingEvent, SetFanStateEvent
from src.domain.models import DeviceMode


class DayOfWeek(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class ScheduleType(Enum):
    LIGHTING = "lighting"
    FAN = "fan"


class LightingScheduleSetting(BaseModel):
    color: tuple[tuple[int, int, int], ...] = Field(..., description="RGB color tuples for LED strips")
    brightness: int = Field(default=100, ge=0, le=100, description="Brightness percentage")


class FanScheduleSetting(BaseModel):
    state: bool = Field(..., description="Fan on/off state")
    speed: Optional[int] = Field(default=None, ge=0, le=100, description="Fan speed percentage")


class Schedule(BaseModel):
    id: str = Field(..., description="Unique schedule identifier")
    name: str = Field(..., description="Human readable schedule name")
    actuator_id: int = Field(..., description="Target actuator ID")
    schedule_type: ScheduleType = Field(..., description="Type of schedule")
    days_of_week: List[DayOfWeek] = Field(..., description="Days when schedule is active")
    start_time: time = Field(..., description="Start time (hour:minute)")
    end_time: time = Field(..., description="End time (hour:minute)")
    setting: Dict[str, Any] = Field(..., description="Schedule-specific settings")
    priority: int = Field(default=0, description="Priority for conflict resolution (higher wins)")
    is_active: bool = Field(default=True, description="Whether schedule is enabled")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True

    def is_active_now(self) -> bool:
        """Check if this schedule should be active at the current time"""
        if not self.is_active:
            return False
            
        now = datetime.now()
        current_day = DayOfWeek(now.weekday())
        current_time = now.time()
        
        # Check if today is in the scheduled days
        if current_day not in self.days_of_week:
            return False
            
        # Handle schedules that cross midnight
        if self.start_time <= self.end_time:
            # Normal case: start_time < end_time (e.g., 09:00 to 17:00)
            return self.start_time <= current_time <= self.end_time
        else:
            # Cross midnight case: start_time > end_time (e.g., 22:00 to 06:00)
            return current_time >= self.start_time or current_time <= self.end_time


class SchedulerService:
    def __init__(self, 
                 event_bus: EventBusInterface,
                 cache_client: CacheClientRepository):
        self.event_bus = event_bus
        self.cache_client = cache_client
        self.schedules: Dict[str, Schedule] = {}
        self.actuator_schedules: Dict[int, List[str]] = {}  # actuator_id -> schedule_ids
        self._scheduler_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the scheduler service"""
        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Scheduler service started")

    async def stop(self):
        """Stop the scheduler service"""
        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler service stopped")

    async def add_schedule(self, schedule: Schedule) -> bool:
        """Add or update a schedule"""
        try:
            self.schedules[schedule.id] = schedule
            
            # Update actuator schedule mapping
            if schedule.actuator_id not in self.actuator_schedules:
                self.actuator_schedules[schedule.actuator_id] = []
            
            if schedule.id not in self.actuator_schedules[schedule.actuator_id]:
                self.actuator_schedules[schedule.actuator_id].append(schedule.id)
            
            logger.info(f"Added/updated schedule {schedule.id} for actuator {schedule.actuator_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding schedule {schedule.id}: {e}")
            return False

    async def remove_schedule(self, schedule_id: str) -> bool:
        """Remove a schedule"""
        try:
            if schedule_id not in self.schedules:
                return False
                
            schedule = self.schedules[schedule_id]
            actuator_id = schedule.actuator_id
            
            # Remove from main schedules dict
            del self.schedules[schedule_id]
            
            # Remove from actuator mapping
            if actuator_id in self.actuator_schedules:
                if schedule_id in self.actuator_schedules[actuator_id]:
                    self.actuator_schedules[actuator_id].remove(schedule_id)
                # Clean up empty lists
                if not self.actuator_schedules[actuator_id]:
                    del self.actuator_schedules[actuator_id]
            
            logger.info(f"Removed schedule {schedule_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing schedule {schedule_id}: {e}")
            return False

    async def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Get a specific schedule"""
        return self.schedules.get(schedule_id)

    async def get_schedules_for_actuator(self, actuator_id: int) -> List[Schedule]:
        """Get all schedules for a specific actuator"""
        schedule_ids = self.actuator_schedules.get(actuator_id, [])
        return [self.schedules[sid] for sid in schedule_ids if sid in self.schedules]

    async def get_all_schedules(self) -> List[Schedule]:
        """Get all schedules"""
        return list(self.schedules.values())

    async def _scheduler_loop(self):
        """Main scheduler loop that runs every minute"""
        while self._running:
            try:
                await self._check_and_apply_schedules()
                # Wait until the next minute
                now = datetime.now()
                seconds_until_next_minute = 60 - now.second
                await asyncio.sleep(seconds_until_next_minute)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    async def _check_and_apply_schedules(self):
        """Check all schedules and apply active ones"""
        try:
            # Group active schedules by actuator
            active_schedules_by_actuator: Dict[int, List[Schedule]] = {}
            
            for schedule in self.schedules.values():
                if schedule.is_active_now():
                    if schedule.actuator_id not in active_schedules_by_actuator:
                        active_schedules_by_actuator[schedule.actuator_id] = []
                    active_schedules_by_actuator[schedule.actuator_id].append(schedule)
            
            # Apply schedules for each actuator
            for actuator_id, active_schedules in active_schedules_by_actuator.items():
                await self._apply_schedules_for_actuator(actuator_id, active_schedules)
                
        except Exception as e:
            logger.error(f"Error checking and applying schedules: {e}")

    async def _apply_schedules_for_actuator(self, actuator_id: int, active_schedules: List[Schedule]):
        """Apply the highest priority active schedule for an actuator"""
        try:
            if not active_schedules:
                return
            
            # Check if actuator is in SCHEDULED mode
            device_id = await self.cache_client.get_device_id_by_actuator_id(actuator_id)
            if not device_id:
                logger.warning(f"Could not find device for actuator {actuator_id}")
                return
            
            device = await self.cache_client.get_device_by_id(device_id)
            if not device:
                logger.warning(f"Could not find device {device_id}")
                return
            
            # Find the actuator and check its mode
            target_actuator = None
            for actuator in device.actuators or []:
                if actuator.id == actuator_id:
                    target_actuator = actuator
                    break
            
            if not target_actuator:
                logger.warning(f"Could not find actuator {actuator_id} in device {device_id}")
                return
            
            if target_actuator.mode != DeviceMode.SCHEDULED:
                logger.debug(f"Actuator {actuator_id} is not in SCHEDULED mode, skipping")
                return
            
            # Sort by priority (highest first), then by updated_at (most recent first)
            active_schedules.sort(key=lambda s: (s.priority, s.updated_at), reverse=True)
            winning_schedule = active_schedules[0]
            
            logger.info(f"Applying schedule {winning_schedule.id} to actuator {actuator_id}")
            
            # Apply the schedule based on type
            if winning_schedule.schedule_type == ScheduleType.LIGHTING:
                await self._apply_lighting_schedule(actuator_id, winning_schedule)
            elif winning_schedule.schedule_type == ScheduleType.FAN:
                await self._apply_fan_schedule(actuator_id, winning_schedule)
            else:
                logger.warning(f"Unknown schedule type: {winning_schedule.schedule_type}")
                
        except Exception as e:
            logger.error(f"Error applying schedules for actuator {actuator_id}: {e}")

    async def _apply_lighting_schedule(self, actuator_id: int, schedule: Schedule):
        """Apply a lighting schedule"""
        try:
            setting = LightingScheduleSetting(**schedule.setting)
            await self.event_bus.publish(SetLightingEvent(
                actuator_id=actuator_id,
                color=setting.color,
                request_id=f"schedule_{schedule.id}"
            ))
        except Exception as e:
            logger.error(f"Error applying lighting schedule {schedule.id}: {e}")

    async def _apply_fan_schedule(self, actuator_id: int, schedule: Schedule):
        """Apply a fan schedule"""
        try:
            setting = FanScheduleSetting(**schedule.setting)
            await self.event_bus.publish(SetFanStateEvent(
                actuator_id=actuator_id,
                state=setting.state,
                request_id=f"schedule_{schedule.id}"
            ))
        except Exception as e:
            logger.error(f"Error applying fan schedule {schedule.id}: {e}") 
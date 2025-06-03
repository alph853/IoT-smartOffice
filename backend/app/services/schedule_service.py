from typing import List, Optional
from datetime import datetime
from loguru import logger

from app.domain.models import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleType
from app.domain.repositories import ScheduleRepository, DeviceRepository
from app.domain.events import EventBusInterface, NotificationEvent
from app.domain.models import Notification, NotificationType, BroadcastMessage


class ScheduleService:
    def __init__(self, 
                 schedule_repo: ScheduleRepository,
                 device_repo: DeviceRepository,
                 event_bus: EventBusInterface):
        self.schedule_repo = schedule_repo
        self.device_repo = device_repo
        self.event_bus = event_bus

    async def start(self):
        logger.info("Schedule service started")

    async def stop(self):
        logger.info("Schedule service stopped")

    async def get_all_schedules(self) -> List[Schedule]:
        """Get all schedules"""
        return await self.schedule_repo.get_all_schedules()

    async def get_schedule_by_id(self, schedule_id: str) -> Optional[Schedule]:
        """Get schedule by ID"""
        return await self.schedule_repo.get_schedule_by_id(schedule_id)

    async def get_schedules_by_actuator_id(self, actuator_id: int) -> List[Schedule]:
        """Get all schedules for a specific actuator"""
        return await self.schedule_repo.get_schedules_by_actuator_id(actuator_id)

    async def create_schedule(self, schedule_create: ScheduleCreate) -> Schedule:
        """Create a new schedule"""
        try:
            # Validate actuator exists
            actuator = await self._validate_actuator(schedule_create.actuator_id)
            if not actuator:
                raise ValueError(f"Actuator {schedule_create.actuator_id} not found")

            # Validate schedule type matches actuator type
            if not self._validate_schedule_type_for_actuator(schedule_create.schedule_type, actuator.type):
                raise ValueError(f"Schedule type {schedule_create.schedule_type.value} not compatible with actuator type {actuator.type}")

            # Validate setting based on schedule type
            self._validate_schedule_setting(schedule_create.schedule_type, schedule_create.setting)

            # Create schedule
            schedule = await self.schedule_repo.create_schedule(schedule_create)
            
            if schedule:
                # Publish notification
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        title="Schedule Created",
                        message=f"Schedule '{schedule.name}' has been created for actuator {schedule.actuator_id}",
                        type=NotificationType.INFO,
                    )
                ))
                
                # Broadcast schedule update
                await self.event_bus.publish(BroadcastMessage(
                    method="scheduleCreated",
                    params={"schedule": schedule},
                ))
            
            return schedule
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            raise

    async def update_schedule(self, schedule_id: str, schedule_update: ScheduleUpdate) -> Optional[Schedule]:
        """Update an existing schedule"""
        try:
            # Check if schedule exists
            existing_schedule = await self.schedule_repo.get_schedule_by_id(schedule_id)
            if not existing_schedule:
                return None

            # Validate actuator if actuator_id is being updated
            if schedule_update.actuator_id and schedule_update.actuator_id != existing_schedule.actuator_id:
                actuator = await self._validate_actuator(schedule_update.actuator_id)
                if not actuator:
                    raise ValueError(f"Actuator {schedule_update.actuator_id} not found")

            # Validate schedule type and setting if being updated
            schedule_type = schedule_update.schedule_type or existing_schedule.schedule_type
            if schedule_update.setting:
                self._validate_schedule_setting(schedule_type, schedule_update.setting)

            # Update schedule
            schedule = await self.schedule_repo.update_schedule(schedule_id, schedule_update)
            
            if schedule:
                # Publish notification
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        title="Schedule Updated",
                        message=f"Schedule '{schedule.name}' has been updated",
                        type=NotificationType.INFO,
                    )
                ))
                
                # Broadcast schedule update
                await self.event_bus.publish(BroadcastMessage(
                    method="scheduleUpdated",
                    params={"schedule": schedule},
                ))
            
            return schedule
        except Exception as e:
            logger.error(f"Error updating schedule {schedule_id}: {e}")
            raise

    async def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule"""
        try:
            # Get schedule info before deleting for notification
            schedule = await self.schedule_repo.get_schedule_by_id(schedule_id)
            if not schedule:
                return False

            success = await self.schedule_repo.delete_schedule(schedule_id)
            
            if success:
                # Publish notification
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        title="Schedule Deleted",
                        message=f"Schedule '{schedule.name}' has been deleted",
                        type=NotificationType.INFO,
                    )
                ))
                
                # Broadcast schedule deletion
                await self.event_bus.publish(BroadcastMessage(
                    method="scheduleDeleted",
                    params={"schedule_id": schedule_id},
                ))
            
            return success
        except Exception as e:
            logger.error(f"Error deleting schedule {schedule_id}: {e}")
            return False

    async def get_active_schedules(self) -> List[Schedule]:
        """Get all active schedules"""
        return await self.schedule_repo.get_active_schedules()

    async def get_schedules_by_type(self, schedule_type: ScheduleType) -> List[Schedule]:
        """Get schedules by type"""
        return await self.schedule_repo.get_schedules_by_type(schedule_type.value)

    async def _validate_actuator(self, actuator_id: int):
        """Validate that actuator exists"""
        try:
            # Get all actuators and find the one with matching ID
            actuators = await self.device_repo.get_all_actuators()
            return next((a for a in actuators if a.id == actuator_id), None)
        except Exception as e:
            logger.error(f"Error validating actuator {actuator_id}: {e}")
            return None

    def _validate_schedule_type_for_actuator(self, schedule_type: ScheduleType, actuator_type: str) -> bool:
        """Validate that schedule type is compatible with actuator type"""
        compatibility_map = {
            ScheduleType.LIGHTING: ["rgb", "led", "light", "lighting"],
            ScheduleType.FAN: ["fan", "cooling"]
        }
        
        compatible_types = compatibility_map.get(schedule_type, [])
        return actuator_type.lower() in compatible_types

    def _validate_schedule_setting(self, schedule_type: ScheduleType, setting: dict):
        """Validate schedule setting based on type"""
        try:
            if schedule_type == ScheduleType.LIGHTING:
                # Validate lighting setting
                if "color" not in setting:
                    raise ValueError("Lighting schedule must have 'color' setting")
                
                color = setting["color"]
                if not isinstance(color, (list, tuple)):
                    raise ValueError("Color must be a list or tuple of RGB tuples")
                
                # Validate each RGB tuple
                for rgb in color:
                    if not isinstance(rgb, (list, tuple)) or len(rgb) != 3:
                        raise ValueError("Each color must be an RGB tuple of 3 values")
                    if not all(isinstance(c, int) and 0 <= c <= 255 for c in rgb):
                        raise ValueError("RGB values must be integers between 0 and 255")
                
                # Validate brightness if present
                if "brightness" in setting:
                    brightness = setting["brightness"]
                    if not isinstance(brightness, int) or not 0 <= brightness <= 100:
                        raise ValueError("Brightness must be an integer between 0 and 100")

            elif schedule_type == ScheduleType.FAN:
                # Validate fan setting
                if "state" not in setting:
                    raise ValueError("Fan schedule must have 'state' setting")
                
                if not isinstance(setting["state"], bool):
                    raise ValueError("Fan state must be a boolean")
                
                # Validate speed if present
                if "speed" in setting and setting["speed"] is not None:
                    speed = setting["speed"]
                    if not isinstance(speed, int) or not 0 <= speed <= 100:
                        raise ValueError("Fan speed must be an integer between 0 and 100")

        except Exception as e:
            logger.error(f"Schedule setting validation failed: {e}")
            raise 
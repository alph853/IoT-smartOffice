from typing import List, Optional
import json
from datetime import time

from app.domain.repositories import ScheduleRepository
from app.domain.models import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleType, DayOfWeek
from app.infra.postgres.db import PostgreSQLConnection
from app.infra.postgres.scripts.sql_schedule import *
from loguru import logger


class PostgresScheduleRepository(ScheduleRepository):
    def __init__(self, db: PostgreSQLConnection):
        self.db = db

    async def get_all_schedules(self) -> List[Schedule]:
        async with self.db.pool.acquire() as conn:
            query = GET_ALL_SCHEDULES
            result = await conn.fetch(query)
            return [self._map_row_to_schedule(row) for row in result]

    async def get_schedule_by_id(self, schedule_id: str) -> Optional[Schedule]:
        async with self.db.pool.acquire() as conn:
            query = GET_SCHEDULE_BY_ID
            result = await conn.fetch(query, schedule_id)
            if result:
                return self._map_row_to_schedule(result[0])
            return None

    async def get_schedules_by_actuator_id(self, actuator_id: int) -> List[Schedule]:
        async with self.db.pool.acquire() as conn:
            query = GET_SCHEDULES_BY_ACTUATOR_ID
            result = await conn.fetch(query, actuator_id)
            return [self._map_row_to_schedule(row) for row in result]

    async def create_schedule(self, schedule: ScheduleCreate) -> Schedule:
        try:
            async with self.db.pool.acquire() as conn:
                query = CREATE_SCHEDULE
                days_of_week = [day.value for day in schedule.days_of_week]
                result = await conn.fetch(
                    query,
                    schedule.name,
                    schedule.actuator_id,
                    schedule.schedule_type.value,
                    days_of_week,
                    schedule.start_time,
                    schedule.end_time,
                    json.dumps(schedule.setting),
                    schedule.priority,
                    schedule.is_active
                )
                if result:
                    return self._map_row_to_schedule(result[0])
                return None
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            raise

    async def update_schedule(self, schedule_id: str, schedule_update: ScheduleUpdate) -> Optional[Schedule]:
        try:
            async with self.db.pool.acquire() as conn:
                query = UPDATE_SCHEDULE
                
                # Convert DayOfWeek enums to integers if provided
                days_of_week = None
                if schedule_update.days_of_week:
                    days_of_week = [day.value for day in schedule_update.days_of_week]
                
                # Convert ScheduleType enum to string if provided
                schedule_type = None
                if schedule_update.schedule_type:
                    schedule_type = schedule_update.schedule_type.value
                
                # Convert setting to JSON if provided
                setting = None
                if schedule_update.setting:
                    setting = json.dumps(schedule_update.setting)
                
                result = await conn.fetch(
                    query,
                    schedule_id,
                    schedule_update.name,
                    schedule_update.actuator_id,
                    schedule_type,
                    days_of_week,
                    schedule_update.start_time,
                    schedule_update.end_time,
                    setting,
                    schedule_update.priority,
                    schedule_update.is_active
                )
                if result:
                    return self._map_row_to_schedule(result[0])
                return None
        except Exception as e:
            logger.error(f"Error updating schedule {schedule_id}: {e}")
            raise

    async def delete_schedule(self, schedule_id: str) -> bool:
        try:
            async with self.db.pool.acquire() as conn:
                query = DELETE_SCHEDULE
                result = await conn.execute(query, schedule_id)
                # asyncpg returns "DELETE n" where n is the number of deleted rows
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting schedule {schedule_id}: {e}")
            return False

    async def get_active_schedules(self) -> List[Schedule]:
        async with self.db.pool.acquire() as conn:
            query = GET_ACTIVE_SCHEDULES
            result = await conn.fetch(query)
            return [self._map_row_to_schedule(row) for row in result]

    async def get_schedules_by_type(self, schedule_type: str) -> List[Schedule]:
        async with self.db.pool.acquire() as conn:
            query = GET_SCHEDULES_BY_TYPE
            result = await conn.fetch(query, schedule_type)
            return [self._map_row_to_schedule(row) for row in result]

    def _map_row_to_schedule(self, row) -> Schedule:
        """Convert database row to Schedule model"""
        try:
            # Convert days_of_week from integer array to DayOfWeek enum list
            days_of_week = [DayOfWeek(day) for day in row['days_of_week']]
            
            # Parse setting JSON
            setting = json.loads(row['setting']) if isinstance(row['setting'], str) else row['setting']
            
            return Schedule(
                id=str(row['id']),
                name=row['name'],
                actuator_id=row['actuator_id'],
                schedule_type=ScheduleType(row['schedule_type']),
                days_of_week=days_of_week,
                start_time=row['start_time'],
                end_time=row['end_time'],
                setting=setting,
                priority=row['priority'],
                is_active=row['is_active'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        except Exception as e:
            logger.error(f"Error mapping row to schedule: {e}, row: {row}")
            raise

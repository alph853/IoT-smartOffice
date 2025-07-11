from typing import List

from app.domain.repositories import NotificationRepository
from app.domain.models import Notification
from app.infra.postgres.db import PostgreSQLConnection
from app.infra.postgres.scripts.sql_notification import *
from loguru import logger


class PostgresNotificationRepository(NotificationRepository):
    def __init__(self, db: PostgreSQLConnection):
        self.db = db

    async def get_all_notifications(self) -> List[Notification]:
        async with self.db.pool.acquire() as conn:
            query = GET_ALL_NOTIFICATION
            result = await conn.fetch(query)
            return [Notification(**row) for row in result]

    async def create_notification(self, notification: Notification) -> Notification:
        try:
            async with self.db.pool.acquire() as conn:
                query = NOTIFICATION_CREATE
                result = await conn.fetch(query,
                                        notification.title,
                                        notification.message,
                                        notification.type,
                                        notification.device_id,
                                        notification.read_status,
                                        notification.ts)
                return Notification(**result[0])
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None

    async def get_notification_by_id(self, notification_id: str) -> Notification | None:
        async with self.db.pool.acquire() as conn:
            query = GET_NOTIFICATION_BY_ID
            result = await conn.fetch(query, notification_id)
            return Notification(**result[0]) if result else None

    async def get_unread_notifications(self) -> List[Notification]:
        async with self.db.pool.acquire() as conn:
            query = GET_UNREAD_NOTIFICATION
            result = await conn.fetch(query)
            return [Notification(**row) for row in result]

    async def mark_all_as_read(self) -> bool:
        async with self.db.pool.acquire() as conn:
            query = NOTIFICATION_MARK_ALL_AS_READ
            result = await conn.execute(query)
            return int(result.split(' ')[-1]) != 0

    async def mark_as_read(self, notification_id: str) -> bool:
        async with self.db.pool.acquire() as conn:
            query = NOTIFICATION_MARK_AS_READ
            result = await conn.execute(query, notification_id)
            return int(result.split(' ')[-1]) != 0

    async def delete_all_notifications(self) -> bool:
        async with self.db.pool.acquire() as conn:
            query = NOTIFICATION_DELETE_ALL
            result = await conn.execute(query)
            return int(result.split(' ')[-1]) != 0

    async def delete_notification(self, notification_id: str) -> bool:
        async with self.db.pool.acquire() as conn:
            query = NOTIFICATION_DELETE
            result = await conn.execute(query, notification_id)
            return int(result.split(' ')[-1]) != 0

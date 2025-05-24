from typing import List

from app.domain.repositories import NotificationRepository
from app.domain.models import Notification
from app.infra.postgres.db import PostgreSQLConnection
from app.infra.postgres.scripts.sql_notification import *


class PostgresNotificationRepository(NotificationRepository):
    def __init__(self, db: PostgreSQLConnection):
        self.db = db

    async def get_all_notifications(self) -> List[Notification]:
        async with self.db.pool.acquire() as conn:
            query = GET_ALL_NOTIFICATIONS
            result = await conn.fetch(query)
            return [Notification(**row) for row in result]

    async def create_notification(self, notification: Notification) -> Notification:
        async with self.db.pool.acquire() as conn:
            query = NOTIFICATION_CREATE
            result = await conn.fetch(query,
                                      notification.title,
                                      notification.message,
                                      notification.type,
                                      notification.device_id,
                                      notification.ts,
                                      notification.read_status)
            return Notification(**result[0])

    async def get_notification_by_id(self, notification_id: str) -> Notification | None:
        async with self.db.pool.acquire() as conn:
            query = GET_NOTIFICATION_BY_ID
            result = await conn.fetch(query, notification_id)
            return Notification(**result[0]) if result else None

    async def get_unread_notifications(self) -> List[Notification]:
        async with self.db.pool.acquire() as conn:
            query = GET_UNREAD_NOTIFICATIONS
            result = await conn.fetch(query)
            return [Notification(**row) for row in result]

    async def mark_all_as_read(self) -> bool:
        async with self.db.pool.acquire() as conn:
            query = NOTIFICATION_MARK_ALL_AS_READ
            result = await conn.fetch(query)
            return int(result.split()[-1]) != 0

    async def mark_as_read(self, notification_id: str) -> bool:
        async with self.db.pool.acquire() as conn:
            query = NOTIFICATION_MARK_AS_READ
            result = await conn.fetch(query, notification_id)
            return True if result else False

    async def delete_all_notifications(self) -> bool:
        async with self.db.pool.acquire() as conn:
            query = NOTIFICATION_DELETE_ALL
            result = await conn.fetch(query)
            return int(result.split()[-1]) != 0

    async def delete_notification(self, notification_id: str) -> bool:
        async with self.db.pool.acquire() as conn:
            query = NOTIFICATION_DELETE
            result = await conn.fetch(query, notification_id)
            return True if result else False

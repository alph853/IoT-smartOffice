from datetime import datetime
from loguru import logger
import asyncio
from typing import List

from app.domain.events import EventBusInterface, NotificationEvent, DeviceConnectedEvent, DeviceDisconnectedEvent
from app.domain.repositories import NotificationRepository, OfficeRepository
from app.domain.models import Notification, NotificationType, BroadcastMessage


class NotificationService:
    def __init__(self, event_bus: EventBusInterface,
                 noti_repo: NotificationRepository,
                 office_repo: OfficeRepository,
                 ):
        self.event_bus = event_bus
        self.noti_repo = noti_repo
        self.office_repo = office_repo

        self.events = {
            DeviceConnectedEvent: self._handle_device_connected_event,
            DeviceDisconnectedEvent: self._handle_device_disconnected_event,
            NotificationEvent: self._handle_notification_event,
        }

    # ---------------------------------------------------------
    # ----------------------- Lifecycle -----------------------
    # ---------------------------------------------------------

    async def start(self):
        await asyncio.gather(
            *[self.event_bus.subscribe(event, handler) for event, handler in self.events.items()]
        )
        logger.info("Notification service started")

    async def stop(self):
        await asyncio.gather(
            *[self.event_bus.unsubscribe(event, handler) for event, handler in self.events.items()]
        )
        logger.info("Notification service stopped")

    # ---------------------------------------------------------
    # ----------------------- Service -------------------------
    # ---------------------------------------------------------

    async def get_all_notifications(self) -> List[Notification]:
        return await self.noti_repo.get_all_notifications()

    async def get_unread_notifications(self) -> List[Notification]:
        return await self.noti_repo.get_unread_notifications()

    async def get_notification_by_id(self, notification_id: int) -> Notification:
        return await self.noti_repo.get_notification_by_id(notification_id)

    async def create_notification(self, notification: Notification) -> Notification:
        return await self.noti_repo.create_notification(notification)

    async def mark_as_read(self, notification_id: int) -> bool:
        return await self.noti_repo.mark_as_read(notification_id)

    async def mark_all_as_read(self) -> bool:
        return await self.noti_repo.mark_all_as_read()

    async def delete_all_notifications(self) -> bool:
        return await self.noti_repo.delete_all_notifications()

    async def delete_notification(self, notification_id: int) -> bool:
        return await self.noti_repo.delete_notification(notification_id)

    # ---------------------------------------------------------
    # ----------------------- Handlers ------------------------
    # ---------------------------------------------------------

    async def _handle_device_connected_event(self, event: DeviceConnectedEvent):
        try:
            device = event.device
            office = await self.office_repo.get_office_by_id(device.office_id)

            notification = Notification(
                title=f"Device {device.name} connected",
                message=f"Device {device.name} ({office.name}) connected successfully. Navigate to device page to view more details.",
                type=NotificationType.INFO,
                device_id=device.id,
            )
            notification = await self.create_notification(notification)
            await self.event_bus.publish(BroadcastMessage(
                method="notification",
                params=notification.model_dump(exclude_none=True),
            ))
        except Exception as e:
            logger.error(f"Error handling device connected event: {e}")

    async def _handle_device_disconnected_event(self, event: DeviceDisconnectedEvent):
        try:
            device = event.device
            office = await self.office_repo.get_office_by_id(device.office_id)

            notification = Notification(
                title=f"Device {device.name} disconnected",
                message=f"Device {device.name} ({office.name}) disconnected normally.",
                type=NotificationType.INFO,
                device_id=device.id,
            )
            notification = await self.create_notification(notification)
            await self.event_bus.publish(BroadcastMessage(
                method="notification",
                params=notification.model_dump(exclude_none=True),
            ))
        except Exception as e:
            logger.error(f"Error handling device disconnected event: {e}")

    async def _handle_notification_event(self, event: NotificationEvent):
        try:
            notification = await self.create_notification(event.notification)
            await self.event_bus.publish(BroadcastMessage(
                method="notification",
                params=notification.model_dump(exclude_none=True),
            ))
        except Exception as e:
            logger.error(f"Error handling notification event: {e}")

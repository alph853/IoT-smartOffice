from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.domain.models import Notification
from app.services import NotificationService
from app.api.dependencies import get_notification_service


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[Notification])
async def get_notifications(
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.get_all_notifications()

@router.get("/unread", response_model=List[Notification])
async def get_unread_notifications(
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.get_unread_notifications()

@router.get("/{notification_id}", response_model=Notification)
async def get_notification(
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.get_notification(notification_id)


@router.post("/", response_model=Notification)
async def create_notification(
    notification: Notification,
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.create_notification(notification)


@router.patch("/mark-all-as-read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_as_read(
    notification_service: NotificationService = Depends(get_notification_service),
):
    if not await notification_service.mark_all_as_read():
        raise HTTPException(status_code=404, detail="No notifications to mark as read")


@router.patch("/mark-as-read/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def mark_as_read(
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
):
    if not await notification_service.mark_as_read(notification_id):
        raise HTTPException(status_code=404, detail="Notification not found")

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_notifications(
    notification_service: NotificationService = Depends(get_notification_service),
):
    if await notification_service.delete_all_notifications():
        raise HTTPException(status_code=404, detail="No notifications to delete")

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
):
    if await notification_service.delete_notification(notification_id):
        raise HTTPException(status_code=404, detail="Notification not found")


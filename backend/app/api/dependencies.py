from fastapi import Request, WebSocket
import aiohttp
from app.services import *



def get_notification_service(request: Request) -> NotificationService:
    return request.app.state.notification_service


def get_device_service(request: Request) -> DeviceService:
    return request.app.state.device_service


def get_broadcast_service(ws: WebSocket) -> BroadcastService:
    return ws.app.state.broadcast_service


def get_office_service(request: Request) -> OfficeService:
    return request.app.state.office_service


def get_session(request: Request) -> aiohttp.ClientSession:
    return request.app.state.session


def get_schedule_service(request: Request) -> ScheduleService:
    return request.app.state.schedule_service

def get_multimedia_service(request: Request) -> MultimediaService:
    return request.app.state.multimedia_service
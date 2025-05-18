from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.services import BroadcastService
from app.api.dependencies import get_broadcast_service


router = APIRouter(prefix="", tags=["ws"])


@router.websocket("/")
async def notifications_ws(
    ws: WebSocket,
    broadcast_service: BroadcastService = Depends(get_broadcast_service),
):
    await broadcast_service.register(ws)

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import asyncio
from loguru import logger
import json

from app.domain.events import EventBusInterface, NotificationEvent
from app.domain.repositories import MqttCloudClientRepository
from app.domain.models import ModeSet, LightingSet, RPCRequest, RPCResponse


class BroadcastService:
    def __init__(self, event_bus: EventBusInterface,
                 cloud_client: MqttCloudClientRepository,
                 ):
        self.clients: List[WebSocket] = []
        self.event_bus: EventBusInterface = event_bus
        self.cloud_client: MqttCloudClientRepository = cloud_client

        self._ws_lock = asyncio.Lock()

        self.events = {
            NotificationEvent: self._handle_notification_event,
        }
        self.handlers = {
            "set_mode": self._set_mode,
            "set_lighting": self._set_lighting,
            "test": self._test,
        }

    async def start(self):
        await asyncio.gather(
            *[self.event_bus.subscribe(event, handler) for event, handler in self.events.items()]
        )

    async def stop(self):
        await asyncio.gather(
            *[self.event_bus.unsubscribe(event, handler) for event, handler in self.events.items()]
        )

    async def register(self, ws: WebSocket):
        try:
            # Accept the websocket connection
            await ws.accept()

            async with self._ws_lock:
                self.clients.append(ws)

            while True:
                try:
                    data = await ws.receive_text()
                    data = json.loads(data)

                    await self.handlers[data["method"]](data)

                except WebSocketDisconnect:
                    logger.info("Client disconnected normally")
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON message: {e}")
                    await ws.send_text(json.dumps({"error": "Invalid JSON format"}))
                except Exception as e:
                    logger.error(f"Error in WebSocket communication: {e}")
                    try:
                        await ws.send_text(json.dumps({"error": str(e)}))
                    except:
                        logger.error("Could not send error response to client")
                    break
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
        finally:
            await self.unregister(ws)

    async def unregister(self, ws: WebSocket):
        async with self._ws_lock:
            if ws in self.clients:
                self.clients.remove(ws)

    # ----------------------------------------------
    # ------------------ Handlers ------------------
    # ----------------------------------------------

    async def _handle_notification_event(self, event: NotificationEvent):
        await self._broadcast(json.dumps(event.notification.model_dump()))

    async def _set_mode(self, request: Dict[str, Any]):
        mode = ModeSet(**request)
        rpc_response = await self.cloud_client.set_mode(mode)
        await self._broadcast(json.dumps(rpc_response.model_dump()))

    async def _set_lighting(self, request: Dict[str, Any]):
        lighting = LightingSet(**request)
        rpc_response = await self.cloud_client.set_lighting(lighting)
        await self._broadcast(json.dumps(rpc_response.model_dump()))

    async def _test(self, request: Dict[str, Any]):
        rpc_response = await self.cloud_client.test_rpc(request)
        await self._broadcast(json.dumps(rpc_response.model_dump()))

    async def _broadcast(self, message: str):
        print(f"Broadcasting message: {message}")
        async with self._ws_lock:
            clients = self.clients.copy()
        await asyncio.gather(*[ws.send_text(message) for ws in clients])

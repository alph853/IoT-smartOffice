from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import asyncio
from loguru import logger
import json

from app.domain.events import EventBusInterface, NotificationEvent
from app.domain.repositories import MqttCloudClientRepository, DeviceRepository
from app.domain.models import LightingSet, ActuatorUpdate, FanStateSet


class BroadcastService:
    def __init__(self, event_bus: EventBusInterface,
                 cloud_client: MqttCloudClientRepository,
                 device_repo: DeviceRepository,
                 ):
        self.clients: List[WebSocket] = []
        self.event_bus = event_bus
        self.cloud_client = cloud_client
        self.device_repo = device_repo

        self._ws_lock = asyncio.Lock()

        self.events = {
            NotificationEvent: self._handle_notification_event,
        }
        self.handlers = {
            "setMode": self._set_mode,
            "setLighting": self._set_lighting,
            "setFanState": self._set_fan_state,
            "setAutoThreshold": self._set_auto_threshold,
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
        params = request["params"]
        update_actuator = ActuatorUpdate(mode=params["mode"])
        if await self.device_repo.update_actuator(params["actuator_id"], update_actuator):
            rpc_response = await self.cloud_client.update_actuator(params["actuator_id"], update_actuator)
            await self._broadcast(json.dumps(rpc_response.model_dump()))
        else:
            await self._broadcast(json.dumps({"error": "Failed to update actuator"}))

    async def _set_lighting(self, request: Dict[str, Any]):
        try:
            lighting_set = LightingSet(**request)
        except Exception as e:
            logger.error(f"Lighting command invalid: {e}")
            await self._broadcast(json.dumps({"error": "Lighting command invalid. Perhaps check your format?"}))
        else:
            rpc_response = await self.cloud_client.set_lighting(lighting_set)
            await self._broadcast(json.dumps(rpc_response.model_dump()))

    async def _set_fan_state(self, request: Dict[str, Any]):
        try:
            fan_state_set = FanStateSet(**request)
        except Exception as e:
            logger.error(f"Fan state command invalid: {e}")
            await self._broadcast(json.dumps({"error": "Fan state command invalid. Perhaps check your format?"}))
        else:
            rpc_response = await self.cloud_client.set_fan_state(fan_state_set)
            await self._broadcast(json.dumps(rpc_response.model_dump()))

    async def _test(self, request: Dict[str, Any]):
        rpc_response = await self.cloud_client.send_rpc_command(request)
        await self._broadcast(json.dumps(rpc_response.model_dump()))

    async def _set_auto_threshold(self, request: Dict[str, Any]):
        try:
            auto_range = AutoRange(**request)
        except Exception as e:
            logger.error(f"Auto range command invalid: {e}")
            await self._broadcast(json.dumps({"error": "Auto range command invalid. Perhaps check your format?"}))
        else:
            rpc_response = await self.cloud_client.set_auto_threshold(auto_range)
            await self._broadcast(json.dumps(rpc_response.model_dump()))

    async def _broadcast(self, message: str):
        print(f"Broadcasting message: {message}")
        async with self._ws_lock:
            clients = self.clients.copy()
        await asyncio.gather(*[ws.send_text(message) for ws in clients])

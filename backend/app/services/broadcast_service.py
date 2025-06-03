from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import asyncio
from loguru import logger
import json
import enum

from app.domain.events import EventBusInterface, NotificationEvent
from app.domain.repositories import MqttCloudClientRepository, DeviceRepository
from app.domain.models import LightingSet, ActuatorUpdate, FanStateSet, BroadcastMessage, Notification, NotificationType, COLOR_MAP
from datetime import datetime


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
            BroadcastMessage: self._handle_broadcast_event,
        }
        self.handlers = {
            "setMode": self._set_mode,
            "setLighting": self._set_lighting,
            "setFanState": self._set_fan_state,
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

            await self.event_bus.publish(NotificationEvent(
                notification=Notification(
                    message="Welcome back to your smart office server!",
                    type=NotificationType.INFO,
                    title="Returner message",
                )
            ))

            while True:
                try:
                    data = await ws.receive_text()
                    data = json.loads(data)

                    await self.handlers[data["method"]](data)

                    logger.info(f"Received message with method: {data['method']}, params: {data['params']}")

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

    # async def _handle_notification_event(self, event: NotificationEvent):
    #     try:
    #         msg = BroadcastMessage(
    #             method="notification",
    #             params=event.notification.model_dump(exclude_none=True),
    #         )
    #         await self._broadcast(msg.model_dump_json())
    #     except Exception as e:
    #         logger.error(f"Error broadcasting notification event: {e}")

    async def _handle_broadcast_event(self, msg: BroadcastMessage):
        try:
            await self._broadcast(msg.model_dump_json(exclude_none=True))
        except Exception as e:
            logger.error(f"Error broadcasting event: {e}")

    async def _set_mode(self, request: Dict[str, Any]):
        params = request["params"]
        update_actuator = ActuatorUpdate(mode=params["mode"])
        if await self.device_repo.update_actuator(params["actuator_id"], update_actuator):
            rpc_response = await self.cloud_client.update_actuator(params["actuator_id"], update_actuator)
            if rpc_response.status == "success":
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        message="Actuator updated successfully",
                        type=NotificationType.INFO,
                        title="Actuator updated",
                    )
                ))
            else:
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        message=f"Failed to update actuator. {rpc_response.data['message']}",
                        type=NotificationType.ERROR,
                        title="Actuator update failed",
                    )
                ))
        else:
            await self.event_bus.publish(NotificationEvent(
                notification=Notification(
                    message="Failed to update actuator",
                    type=NotificationType.ERROR,
                    title="Actuator update failed",
                )
            ))

    async def _set_lighting(self, request: Dict[str, Any]):
        try:
            lighting_set = LightingSet(**request)
            lighting_set = self._transform_lighting_set(lighting_set)
            actuator_update = ActuatorUpdate(setting={"color": lighting_set.params.color})
            if not await self.device_repo.update_actuator(lighting_set.params.actuator_id, actuator_update):
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        message="Lighting set failed. Perhaps you're trying to control the light in automode. Please switch to manual mode.",
                        type=NotificationType.ERROR,
                        title="Lighting set failed",
                    )
                ))
                return
        except Exception as e:
            logger.error(f"Lighting command invalid: {e}")
            await self.event_bus.publish(NotificationEvent(
                notification=Notification(
                    message="Lighting command invalid. Perhaps check your format?",
                    type=NotificationType.ERROR,
                    title="Lighting command invalid",
                )
            ))
        else:
            rpc_response = await self.cloud_client.set_lighting(lighting_set)
            if rpc_response.status == "success":
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        message="Lighting set successfully",
                        type=NotificationType.INFO,
                        title="Lighting set",
                    )
                ))
            else:
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        message=f"Failed to set lighting. {rpc_response.data['message']}",
                        type=NotificationType.ERROR,
                        title="Lighting set failed",
                    )
                ))

    async def _set_fan_state(self, request: Dict[str, Any]):
        try:
            fan_state_set = FanStateSet(**request)
            actuator_update = ActuatorUpdate(setting=fan_state_set.params.model_dump())
            if not await self.device_repo.update_actuator(fan_state_set.params.actuator_id, actuator_update):
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        message="Fan state set failed. Maybe you're trying to control the fan in automode. Please switch to manual mode.",
                        type=NotificationType.ERROR,
                        title="Fan state set failed",
                    )
                ))
                return
        except Exception as e:
            logger.error(f"Fan state command invalid: {e}")
            await self.event_bus.publish(NotificationEvent(
                notification=Notification(
                    message="Fan state command invalid. Perhaps check your format?",
                    type=NotificationType.ERROR,
                    title="Fan state command invalid",
                )
            ))
        else:
            rpc_response = await self.cloud_client.set_fan_state(fan_state_set)
            if rpc_response.status == "success":
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        message="Fan state set successfully",
                        type=NotificationType.INFO,
                        title="Fan state set",
                    )
                ))
            else:
                await self.event_bus.publish(NotificationEvent(
                    notification=Notification(
                        message=f"Failed to set fan state. {rpc_response.data['message']}",
                        type=NotificationType.ERROR,
                        title="Fan state set failed",
                    )
                ))

    async def _test(self, request: Dict[str, Any]):
        rpc_response = await self.cloud_client.send_rpc_command(request)
        if rpc_response.status == "success":
            await self.event_bus.publish(NotificationEvent(
                notification=Notification(
                    message="RPC command sent successfully",
                    type=NotificationType.INFO,
                    title="RPC command sent",
                )
            ))
        else:
            await self.event_bus.publish(NotificationEvent(
                notification=Notification(
                    message=f"Failed to send RPC command. {rpc_response.data['message']}",
                    type=NotificationType.ERROR,
                    title="RPC command sent failed",
                )
            ))

    async def _broadcast(self, message: str):
        async with self._ws_lock:
            clients = self.clients.copy()
        await asyncio.gather(*[ws.send_text(message) for ws in clients])

    def _transform_lighting_set(self, lighting_set: LightingSet):
        color = lighting_set.params.color
        brightness = lighting_set.params.brightness
        lighting_set.params.color = tuple(map(lambda x: tuple(map(lambda y: int(y * brightness / 100), x if not isinstance(x, enum.Enum) else COLOR_MAP[x.value])), color))
        lighting_set.params.brightness = 100
        return lighting_set
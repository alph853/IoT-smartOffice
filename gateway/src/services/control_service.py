from loguru import logger
from typing import Dict
import asyncio

from src.domain.events import *
from src.domain.repositories import MqttGatewayClientRepository, CacheClientRepository, MqttCloudClientRepository
from src.domain.models import RPCResponse


class ControlService:
    def __init__(self, event_bus: EventBusInterface,
                 gw_client: MqttGatewayClientRepository,
                 cache_client: CacheClientRepository,
                 cloud_client: MqttCloudClientRepository,
                 ):
        self.event_bus = event_bus
        self.gw_client = gw_client
        self.cache_client = cache_client
        self.cloud_client = cloud_client

    async def start(self):
        self.events = {
            DeleteDeviceEvent: self._handle_delete_device,
            UpdateDeviceEvent: self._handle_update_device,
            GatewayDeviceDeletedEvent: self._handle_gateway_device_deleted,
            UpdateActuatorEvent: self._handle_update_actuator,
            SetLightingEvent: self._handle_set_lighting,
            SetFanStateEvent: self._handle_set_fan_state,
            RPCTestEvent: self._handle_rpc_test,
            InvalidRPCEvent: self._handle_invalid_rpc,
            UnknownEvent: self._handle_unknown,
        }
        await asyncio.gather(*[
            self.event_bus.subscribe(event, handler) for event, handler in self.events.items()
        ])


    async def stop(self):
        await asyncio.gather(*[
            self.event_bus.unsubscribe(event, handler) for event, handler in self.events.items()
        ])

    async def _handle_delete_device(self, event: DeleteDeviceEvent):
        try:
            device = await self.cache_client.get_device_by_id(event.device_id)
            response = None
            if device:
                print(type(event.request_id), type(event.device_id))
                if await self.cache_client.delete_device(event.device_id):
                    await self.gw_client.disconnect_device(device.id)
                    response = RPCResponse(status="success", data={"message": "Device disconnected"})
                else:
                    response = RPCResponse(status="error", data={"message": "Device deletion failed"})
            else:
                response = RPCResponse(status="error", data={"message": "Device not found"})
            print(response)
            self.cloud_client.send_rpc_reply(event.request_id, response.model_dump(mode='json'))
        except Exception as e:
            logger.error(f"Error handling delete device event: {e}")

    async def _handle_update_device(self, event: UpdateDeviceEvent):
        try:
            device_id = event.device_id
            device = await self.cache_client.get_device_by_id(device_id)
            if device:
                status = event.device_update.get("status", None)
                if status == "disabled":
                    await self.gw_client.disconnect_device(device.id)
                    if await self.cache_client.update_device(device_id, event.device_update):
                        response = RPCResponse(status="success", data={"message": "Device updated"})
                elif status == "online":
                    await self.gw_client.connect_device(device.id)
                    if await self.cache_client.update_device(device_id, event.device_update):
                        response = RPCResponse(status="success", data={"message": "Device updated"})
            else:
                response = RPCResponse(status="error", data={"message": "Device not found"})
            self.cloud_client.send_rpc_reply(event.request_id, response.model_dump())
        except Exception as e:
            logger.error(f"Update device service error: {e}")

    async def _handle_gateway_device_deleted(self, event: GatewayDeviceDeletedEvent):
        pass

    async def _handle_update_actuator(self, event: UpdateActuatorEvent):
        try:
            print("-"*50)
            print(event)
            actuator_id = event.actuator_id
            if await self.cache_client.update_actuator(actuator_id, event.actuator_update):
                response = RPCResponse(status="success", data={"message": "Actuator updated"})
            else:
                response = RPCResponse(status="error", data={"message": "Actuator not found"})
        except Exception as e:
            logger.error(f"Update actuator service error: {e}")
            response = RPCResponse(status="error", data={"message": "Actuator not found"})
        finally:
            self.cloud_client.send_rpc_reply(event.request_id, response.model_dump())

    async def _handle_set_lighting(self, event: SetLightingEvent):
        try:
            if await self.gw_client.set_lighting(event):
                response = RPCResponse(status="success", data={"message": "Lighting updated"})
            else:
                response = RPCResponse(status="error", data={"message": "Failed to set lighting"})
            self.cloud_client.send_rpc_reply(event.request_id, response.model_dump())
        except Exception as e:
            logger.error(f"Set lighting service error: {e}")

    async def _handle_set_fan_state(self, event: SetFanStateEvent):
        try:
            if await self.gw_client.set_fan_state(event):
                response = RPCResponse(status="success", data={"message": "Fan state updated"})
            else:
                response = RPCResponse(status="error", data={"message": "Device not found"})
            self.cloud_client.send_rpc_reply(event.request_id, response.model_dump())
        except Exception as e:
            logger.error(f"Set fan service error: {e}")

    async def _handle_rpc_test(self, event: RPCTestEvent):
        try:
            if await self.gw_client.send_test_command(event):
                response = RPCResponse(status="success", data={"message": "Test event received"})
            else:
                response = RPCResponse(status="error", data={"message": "Device not found"})
            self.cloud_client.send_rpc_reply(event.request_id, response.model_dump())
        except Exception as e:
            logger.error(f"RPC test service error: {e}")

    async def _handle_invalid_rpc(self, event: InvalidRPCEvent):
        try:
            response = RPCResponse(status="error", data={"message": "Invalid RPC event"})
            self.cloud_client.send_rpc_reply(event.request_id, response.model_dump())
        except Exception as e:
            logger.error(f"Handle invalid rpc service error: {e}")

    async def _handle_unknown(self, event: UnknownEvent):
        try:
            response = RPCResponse(status="error", data={"message": "Unknown RPC event"})
            self.cloud_client.send_rpc_reply(event.request_id, response.model_dump())
        except Exception as e:
            logger.error(f"Handle unknown service error: {e}")
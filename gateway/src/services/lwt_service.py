from loguru import logger
from typing import Dict
import asyncio

from src.domain.repositories import MqttGatewayClientRepository, CacheClientRepository, HttpClientRepository
from src.domain.events import EventBusInterface
from src.domain.models import DeviceStatus


class LWTService:
    """Service to handle Last Will and Testament messages from devices"""
    
    def __init__(self, 
                 event_bus: EventBusInterface,
                 cache_client: CacheClientRepository,
                 http_client: HttpClientRepository,
                 mqtt_gateway_client: MqttGatewayClientRepository):
        self.event_bus = event_bus
        self.cache_client = cache_client
        self.http_client = http_client
        self.mqtt_gateway_client = mqtt_gateway_client
        self.lwt_topic = None
        self.startup_grace_period = 3  # seconds to ignore LWT messages after startup
        self.startup_time = None

    async def start(self):
        """Start the LWT service and subscribe to LWT topic"""
        try:
            topics = await self.mqtt_gateway_client.get_topics()
            self.lwt_topic = topics.get("lwt", {}).get("topic", "gateway/lwt")
            
            # Set startup time for grace period
            import time
            self.startup_time = time.time()
            
            # Subscribe without receiving retained messages
            await self.mqtt_gateway_client.subscribe_without_retained(self.lwt_topic, self._handle_lwt_message)
            logger.info(f"LWT service started, subscribed to {self.lwt_topic} (no retained messages)")
        except Exception as e:
            logger.error(f"Failed to start LWT service: {e}")

    async def stop(self):
        """Stop the LWT service"""
        if self.lwt_topic:
            await self.mqtt_gateway_client.unsubscribe(self.lwt_topic)
        logger.info("LWT service stopped")

    async def _handle_lwt_message(self, message: Dict):
        """Handle LWT message from disconnected device"""
        try:
            # Check if we're in the startup grace period
            if self.startup_time is not None:
                import time
                if time.time() - self.startup_time < self.startup_grace_period:
                    logger.debug(f"Ignoring LWT message during startup grace period: {message.get('payload', '').strip()}")
                    return
            
            mac_address = message.get("payload", "").strip()
            
            if not mac_address:
                logger.warning("Received empty LWT message")
                return
                
            logger.info(f"Received LWT for device with MAC: {mac_address}")
            device = await self.cache_client.get_device_by_mac(mac_address)
            
            if not device:
                logger.warning(f"Device with MAC {mac_address} not found in cache")
                return
        
            if device.status != DeviceStatus.ONLINE.value:
                logger.info(f"Device {device.name} (MAC: {mac_address}) is already {device.status}")
                return

            await self.cache_client.update_device(device.id, {"status": DeviceStatus.OFFLINE.value})
            
            try:
                await self.http_client.set_device_status(device.id, DeviceStatus.OFFLINE)
            except Exception as e:
                logger.error(f"Failed to notify backend of LWT event: {e}")

            logger.info(f"Device {device.name} (MAC: {mac_address}) marked as offline due to LWT")
            
        except Exception as e:
            logger.error(f"Error handling LWT message: {e}") 
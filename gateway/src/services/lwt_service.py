from loguru import logger
from typing import Dict

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

    async def start(self):
        """Start the LWT service and subscribe to LWT topic"""
        try:
            # Get LWT topic from config
            topics = await self.mqtt_gateway_client.get_topics()
            self.lwt_topic = topics.get("lwt", {}).get("topic", "gateway/lwt")
            
            # Subscribe to LWT topic
            await self.mqtt_gateway_client.subscribe(self.lwt_topic, self._handle_lwt_message)
            logger.info(f"LWT service started, subscribed to {self.lwt_topic}")
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
            # Extract MAC address from message payload
            mac_address = message.get("payload", "").strip()
            
            if not mac_address:
                logger.warning("Received empty LWT message")
                return
                
            logger.info(f"Received LWT for device with MAC: {mac_address}")
            
            # Get device from cache by MAC address
            device = await self.cache_client.get_device_by_mac(mac_address)
            
            if not device:
                logger.warning(f"Device with MAC {mac_address} not found in cache")
                return
            
            # Update device status to offline in cache
            device.status = DeviceStatus.OFFLINE
            await self.cache_client.set_device(device)
            
            # Update device status in backend
            update_data = {
                "status": DeviceStatus.OFFLINE.value
            }
            
            await self.http_client.update_device(device.id, update_data)
            
            logger.info(f"Device {device.name} (MAC: {mac_address}) marked as offline")
            
        except Exception as e:
            logger.error(f"Error handling LWT message: {e}") 
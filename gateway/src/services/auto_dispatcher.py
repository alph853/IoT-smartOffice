from src.domain.events import EventBusInterface
from src.domain.repositories import MqttGatewayClientRepository


class AutoDispatcherService:
    def __init__(self, gw_client: MqttGatewayClientRepository, event_bus: EventBusInterface):
        self.mqtt_client = gw_client
        self.event_bus = event_bus

    def dispatch(self, message: str):
        pass
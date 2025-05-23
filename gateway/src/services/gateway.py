from src.domain.repositories import MqttGatewayClientRepository, MqttCloudClientRepository
from src.domain.events import EventBusInterface


class GatewayService:
    def __init__(self,
                 gw_client: MqttGatewayClientRepository,
                 cloud_client: MqttCloudClientRepository,
                 event_bus: EventBusInterface,
                 ):
        self.gw_client = gw_client
        self.cloud_client = cloud_client
        self.event_bus = event_bus

    def dispatch(self, message: str):
        pass
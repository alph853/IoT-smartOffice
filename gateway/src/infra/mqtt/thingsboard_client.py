from typing import List

from src.domain.events import EventBusInterface
from src.domain.models import MqttTopic
from src.domain.repositories import MqttCloudClientRepository


class ThingsboardClient(MqttCloudClientRepository):
    def __init__(self, broker_url: str,
                 password: str,
                 topics: List[MqttTopic],
                 event_bus: EventBusInterface,
                 broker_port: int = 1883,
                 client_id: str = "",
                 username: str = "",
                 ):

        self.broker_url = broker_url
        self.broker_port = broker_port
        self.client_id = client_id

        self.username = username
        self.password = password
        self.event_bus = event_bus
        self.topics    = topics

    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    @property
    def messages(self):
        pass


    # -------------------------------------------------------------
    # ------------------------- Publish -------------------------
    # -------------------------------------------------------------

    def publish_telemetry(self, topic: str, payload: str, qos: int, retain: bool):
        pass

    def publish_rpc_response(self, topic: str, payload: str, qos: int, retain: bool):
        pass
    
    def publish_rpc_request(self, topic: str, payload: str, qos: int, retain: bool):
        pass
    
    
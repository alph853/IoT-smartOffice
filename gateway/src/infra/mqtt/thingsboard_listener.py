from src.domain.events import EventBusInterface
from src.infra.mqtt import ThingsboardClient
from aiomqtt import MessagesIterator


class ThingsboardListener:
    def __init__(self, msg_generator: MessagesIterator, event_bus: EventBusInterface):
        self.msg_generator = msg_generator
        self.event_bus = event_bus

    # -------------------------------------------------------------
    # ------------------------- Lifecycle -------------------------
    # -------------------------------------------------------------

    async def start(self):
        pass

    async def stop(self):
        pass
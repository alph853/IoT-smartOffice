import asyncio
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type
from abc import ABC, abstractmethod

EventHandler = Callable[[Any], asyncio.Future]


class EventBusInterface(ABC):

    @abstractmethod
    async def subscribe(self, event_type: Type, handler: EventHandler) -> None:
        pass

    @abstractmethod
    async def unsubscribe(self, event_type: Type, handler: EventHandler) -> None:
        pass

    @abstractmethod
    async def publish(self, event: Any) -> None:
        pass





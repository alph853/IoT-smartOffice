import asyncio
from collections import defaultdict
from typing import Any, Dict, List, Type

from src.domain.events import EventBusInterface, EventHandler


class InProcEventBus(EventBusInterface):
    def __init__(self):
        self._subscribers: Dict[Type, List[EventHandler]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, event_type: Type, handler: EventHandler) -> None:
        async with self._lock:
            self._subscribers[event_type].append(handler)

    async def unsubscribe(self, event_type: Type, handler: EventHandler) -> None:
        async with self._lock:
            self._subscribers[event_type].remove(handler)

    async def publish(self, event: Any) -> None:
        async with self._lock:
            handlers = list(self._subscribers.get(type(event), []))
        await asyncio.gather(*[handler(event) for handler in handlers], return_exceptions=True)





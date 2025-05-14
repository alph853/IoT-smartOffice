from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import ControlCommand


class ControlRepository(ABC):
    @abstractmethod
    async def save_command(self, command: ControlCommand) -> None:
        pass

    @abstractmethod
    async def get_command(self, command_id: str) -> Optional[ControlCommand]:
        pass

    @abstractmethod
    async def get_pending_commands(self) -> List[ControlCommand]:
        pass

    @abstractmethod
    async def update_command_status(self, command_id: str, status: str) -> None:
        pass

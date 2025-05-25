from abc import ABC, abstractmethod
from typing import List
from app.domain.models import Office


class OfficeRepository(ABC):
    @abstractmethod
    async def get_all_offices(self) -> List[Office]:
        pass

    @abstractmethod
    async def get_office_by_id(self, office_id: int) -> Office:
        pass

    @abstractmethod
    async def create_office(self, office: Office) -> Office:
        pass

    @abstractmethod
    async def update_office(self, office_id: int, office: Office) -> Office:
        pass

    @abstractmethod
    async def delete_office(self, office_id: int) -> bool:
        pass

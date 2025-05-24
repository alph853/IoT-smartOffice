from abc import ABC, abstractmethod

from app.domain.models import Office


class OfficeRepository(ABC):
    @abstractmethod
    async def get_office_by_id(self, office_id: int) -> Office:
        pass
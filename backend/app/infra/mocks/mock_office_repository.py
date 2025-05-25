from typing import List, Optional
from loguru import logger

from app.domain.models import Office
from app.domain.repositories import OfficeRepository


class MockOfficeRepository(OfficeRepository):
    def __init__(self):
        self.offices: List[Office] = []

    async def get_all_offices(self) -> List[Office]:
        logger.info("Mock: Getting all offices")
        return self.offices

    async def get_office_by_id(self, office_id: int) -> Optional[Office]:
        logger.info(f"Mock: Getting office by ID {office_id}")
        return next((o for o in self.offices if o.id == office_id), None)

    async def create_office(self, office: Office) -> Office:
        logger.info(f"Mock: Creating office {office}")
        self.offices.append(office)
        return office

    async def update_office(self, office_id: int, office: Office) -> Office:
        logger.info(f"Mock: Updating office {office_id}")
        for i, o in enumerate(self.offices):
            if o.id == office_id:
                self.offices[i] = office
                return office
        return office

    async def delete_office(self, office_id: int) -> bool:
        logger.info(f"Mock: Deleting office {office_id}")
        initial_length = len(self.offices)
        self.offices = [o for o in self.offices if o.id != office_id]
        return len(self.offices) < initial_length

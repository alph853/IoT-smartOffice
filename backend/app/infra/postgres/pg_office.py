from typing import List

from app.domain.models import Office
from app.domain.repositories import OfficeRepository
from app.infra.postgres.db import PostgreSQLConnection
from app.infra.postgres.scripts.sql_office import GET_ALL_OFFICES, GET_OFFICE_BY_ID, CREATE_OFFICE, UPDATE_OFFICE, DELETE_OFFICE


class PostgresOfficeRepository(OfficeRepository):
    def __init__(self, db: PostgreSQLConnection):
        self.db = db

    async def get_all_offices(self) -> List[Office]:
        async with self.db.acquire() as conn:
            query = GET_ALL_OFFICES
            result = await conn.fetch(query)
            return [Office(**row) for row in result]

    async def get_office_by_id(self, office_id: int) -> Office:
        async with self.db.acquire() as conn:
            query = GET_OFFICE_BY_ID
            result = await conn.fetch(query, office_id)
            return Office(**result[0])

    async def create_office(self, office: Office) -> Office:
        async with self.db.acquire() as conn:
            query = CREATE_OFFICE

    async def update_office(self, office_id: int, office: Office) -> Office:
        async with self.db.acquire() as conn:
            query = UPDATE_OFFICE
            result = await conn.fetch(query, office_id, office.name, office.description)
            return Office(**result[0])

    async def delete_office(self, office_id: int) -> bool:
        async with self.db.acquire() as conn:
            query = DELETE_OFFICE
            result = await conn.fetch(query, office_id)
            return result[0]
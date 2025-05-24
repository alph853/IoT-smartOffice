from app.domain.models import Office
from app.domain.repositories import OfficeRepository
from app.infra.postgres.db import PostgreSQLConnection
from app.infra.postgres.scripts.sql_office import GET_OFFICE_BY_ID


class PostgresOfficeRepository(OfficeRepository):
    def __init__(self, db: PostgreSQLConnection):
        self.db = db

    async def get_office_by_id(self, office_id: int) -> Office:
        async with self.db.acquire() as conn:
            query = GET_OFFICE_BY_ID
            result = await conn.fetch(query, office_id)
            return Office(**result[0])

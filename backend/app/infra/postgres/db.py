import asyncio
import asyncpg
from contextlib import asynccontextmanager
from loguru import logger


class PostgreSQLConnection:
    """
    """
    def __init__(self,
                 host: str,
                 port: int,
                 user: str,
                 password: str,
                 database: str
                 ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.pool = None
        self._lock = asyncio.Lock()

    async def initialize(self):
        if self.pool is None:
            async with self._lock:
                if self.pool is None:
                    self.pool = await asyncpg.create_pool(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        database=self.database
                    )
                    logger.info("PostgreSQL connection pool initialized")

    @asynccontextmanager
    async def acquire(self):
        if self.pool is None:
            await self.initialize()

        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            await self.pool.release(conn)

    async def close(self):
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
            logger.info("PostgreSQL connection pool closed")


if __name__ == "__main__":
    DB = PostgreSQLConnection(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    asyncio.run(DB.initialize())

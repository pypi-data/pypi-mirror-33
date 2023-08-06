import asyncpg
import threading

from async_generator import asynccontextmanager
from longitude import config
from collections import OrderedDict
from .sql import SQLFetchable
from longitude.utils import allow_sync


class PostgresqlModel(SQLFetchable):

    def __init__(self, pool):
        # The connection has to be local because has to
        # be tied to the thread's event loop
        self.thead_locals = threading.local()
        self.thead_locals.pool = pool

    async def get_poll(self):

        # If the current thread has no conn, try to
        # create it from the current thread's event loop
        if not hasattr(self.thead_locals, 'pool'):
            self.thead_locals.pool = await self._create_pool()

        return self.thead_locals.pool

    @classmethod
    async def instantiate(cls):
        return cls(await cls._create_pool())

    @staticmethod
    async def _create_pool():
        return await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            host=config.DB_HOST,
            port=config.DB_PORT,
        )

    @asynccontextmanager
    async def get_conn(self):
        pool = await self.get_poll()
        conn = await pool.acquire(timeout=10)
        yield conn
        await pool.release(conn)

    @allow_sync
    async def fetch(self, *args, **kwargs):
        # TODO: allow the connection to be passed as
        # argument

        conn = kwargs.pop('conn', None)

        if conn is not None:
            res = await conn.fetch(*args, **kwargs)
        else:
            async with self.get_conn() as conn:
                res = await conn.fetch(*args, **kwargs)

        return [
            OrderedDict(x.items())
            for x
            in res
        ]

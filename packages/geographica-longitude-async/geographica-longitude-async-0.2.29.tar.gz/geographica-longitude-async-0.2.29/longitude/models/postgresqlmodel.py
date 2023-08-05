import asyncpg
import threading

from longitude import config
from collections import OrderedDict
from .sql import SQLFetchable
from longitude.utils import allow_sync


class PostgresqlModel(SQLFetchable):

    def __init__(self, conn):
        # The connection has to be local because has to
        # be tied to the thread's event loop
        self.thead_locals = threading.local()
        self.thead_locals.conn = conn

    async def get_conn(self):

        # If the current thread has no conn, try to
        # create it from the current thread's event loop
        if not hasattr(self.thead_locals, 'conn'):
            self.thead_locals.conn = await self.create_connection()

        return self.thead_locals.conn

    @classmethod
    async def instantiate(cls):
        return cls(await cls.create_connection())

    @staticmethod
    async def create_connection():
        return await asyncpg.connect(
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            host=config.DB_HOST,
            port=config.DB_PORT,
        )

    @allow_sync
    async def fetch(self, *args, **kwargs):
        conn = await self.get_conn()
        res = await conn.fetch(*args, **kwargs)

        return [
            OrderedDict(x.items())
            for x
            in (res)
        ]

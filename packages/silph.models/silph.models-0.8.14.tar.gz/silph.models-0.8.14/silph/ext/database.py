import re
import asyncio
import logging

log = logging.getLogger('silph.ext.database')


class Database(object):
    def __init__(self, redis_url=None, mysql_url=None, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.redis_url = redis_url
        self.mysql_url = mysql_url

    def connect(self):
        connections = []

        if self.redis_url:
            connections.append(self.connect_redis())

        if self.mysql_url:
            connections.append(self.connect_mysql())

        tasks = asyncio.gather(*connections)
        self.loop.run_until_complete(tasks)

    def close(self):
        closes = []

        if self.mysql_url:
            closes.append(self.mysql.close())

        if self.redis_url:
            self.redis.close()
            closes.append(self.redis.wait_closed())

        tasks = asyncio.gather(*closes)
        self.loop.run_until_complete(tasks)

    async def connect_redis(self):

        import aioredis

        log.debug('Creating Redis instance')

        self.redis = await aioredis.create_redis_pool(
            self.redis_url,
            encoding='utf8',
            minsize=5,
            maxsize=25,
        )

    async def connect_mysql(self):

        from asyncqlio import DatabaseInterface
        from silph.models.base import Table

        log.debug('Creating MySQL instance')

        self.mysql = DatabaseInterface(self.mysql_url)
        await self.mysql.connect()

        log.debug('Binding MySQL to ORM')
        self.mysql.bind_tables(Table.metadata)

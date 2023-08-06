from motor.motor_asyncio import AsyncIOMotorClient

from .. import EtcdMixin


class Mongo(AsyncIOMotorClient, EtcdMixin):
    pass

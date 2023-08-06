from motor.motor_asyncio import AsyncIOMotorClient

from .. import EtcdMixin


class Mongodb(AsyncIOMotorClient, EtcdMixin):
    pass

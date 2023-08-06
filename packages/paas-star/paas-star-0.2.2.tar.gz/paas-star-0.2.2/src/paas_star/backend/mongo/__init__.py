import typing

from functools import partial
from star_builder import Component

from .mongo import Mongo
from .. import Manager

SERVICE_NAME = "MONGO"
MongoManger = typing.NewType("MongoManger", Manager)


class MongoMangerComponent(Component):

    def resolve(self) -> MongoManger:
        return MongoManger(
            Manager(partial(Mongo.from_etcd, SERVICE_NAME)))


class MongoComponent(Component):

    def resolve(self) -> Mongo:
        return Mongo.from_etcd(SERVICE_NAME)

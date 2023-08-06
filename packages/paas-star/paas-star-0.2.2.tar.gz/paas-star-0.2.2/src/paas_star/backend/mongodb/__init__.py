import typing

from functools import partial
from star_builder import Component

from .. import Manager
from .mongodb import Mongodb

SERVICE_NAME = "mongodb"
MongodbManger = typing.NewType("MongodbManger", Manager)


class MongodbMangerComponent(Component):

    def resolve(self) -> MongodbManger:
        return MongodbManger(
            Manager(partial(Mongodb.from_etcd, SERVICE_NAME)))


class MongodbComponent(Component):

    def resolve(self) -> Mongodb:
        return Mongodb.from_etcd(SERVICE_NAME)

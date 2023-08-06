import typing

from functools import partial
from star_builder import Component

from .. import Manager
from .routing import Routing

SERVICE_NAME = "routing"

RoutingManger = typing.NewType("RoutingManger", Manager)


class RoutingMangerComponent(Component):

    def resolve(self) -> RoutingManger:
        return RoutingManger(
            Manager(partial(Routing.from_etcd, SERVICE_NAME)))


class MongoComponent(Component):

    def resolve(self) -> Routing:
        return Routing.from_etcd(SERVICE_NAME)

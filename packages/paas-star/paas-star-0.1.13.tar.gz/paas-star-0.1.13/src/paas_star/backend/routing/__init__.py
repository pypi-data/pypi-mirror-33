from random import choice
from star_builder import Component

from archsdk import get_service

from .routing import Routing


class RoutingComponent(Component):

    def resolve(self) -> Routing:
        return Routing(**choice(get_service("routing")))

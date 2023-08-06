from random import choice
from star_builder import Component

from archsdk import get_service

from .mongodb import Mongodb


class MongodbComponent(Component):

    def resolve(self) -> Mongodb:
        return Mongodb(**choice(get_service("mongodb")))

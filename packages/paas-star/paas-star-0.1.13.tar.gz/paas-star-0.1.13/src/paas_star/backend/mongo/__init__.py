from random import choice
from star_builder import Component

from archsdk import get_service

from .mongo import Mongo


class MongoComponent(Component):

    def resolve(self) -> Mongo:
        return Mongo(**choice(get_service("MONGO")))
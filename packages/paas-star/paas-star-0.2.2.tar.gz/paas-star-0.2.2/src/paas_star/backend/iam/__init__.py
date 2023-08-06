from star_builder import Component

from .iam import Iam
from ..routing.routing import Routing


class IamComponent(Component):

    def resolve(self, routing: Routing) -> Iam:
        return Iam(routing)

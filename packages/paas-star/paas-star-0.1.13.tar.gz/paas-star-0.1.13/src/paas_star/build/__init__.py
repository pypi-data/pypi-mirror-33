from os.path import join, abspath, dirname
from star_builder.build import Command, find_tasks, Task

from .tasks import *


class PaasCommand(Command):

    def __init__(self, tasks):
        for name, prop in globals().items():
            if prop is not Task and \
                    isinstance(prop, type) and \
                    issubclass(prop, Task):
                tasks[name.lower()] = prop
        super(PaasCommand, self).__init__(tasks)
        self.templates.insert(
            1, join(abspath(dirname(dirname(__file__))), "templates"))


def main():
    PaasCommand(find_tasks()).create()

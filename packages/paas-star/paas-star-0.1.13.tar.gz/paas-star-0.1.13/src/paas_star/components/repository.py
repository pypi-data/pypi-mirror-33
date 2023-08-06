from toolkit import _find_caller_name
from star_builder import Service

from .session import Session
from ..logger import get_logger


class Repository(Service):

    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name", _find_caller_name())
        self.logger = get_logger(name)

    def resolve(self, session: Session):
        """
        每次请求都更新logger.user
        :param session:
        :return:
        """
        self.logger.user = session.user

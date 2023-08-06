from random import choice
from urllib.parse import urljoin
from toolkit import cache_property
from archsdk import get_service

from ..logger import get_logger


class Manager(object):

    def __init__(self, callback):
        self.callback = callback
        self._instance = callback()
        self.reload = False

    def __call__(self, reload=False):
        self.reload = reload
        return self

    def __enter__(self):
        if self.reload:
            self._instance = self.callback()
        return self._instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and not self.reload:
            self._instance = self.callback()
        return exc_type is None


class EtcdMixin(object):
    callback = None

    @classmethod
    def from_etcd(cls, service=None):
        if service:
            cls.callback = lambda: choice(get_service(service))
        return cls(**cls.callback())


class LoggerMixin(object):

    @cache_property
    def logger(self):
        """
        可以选择覆盖这个属性
        :return:
        """
        return get_logger("unset")

    def set_logger(self, logger):
        self.logger = logger


class RestfulApi(EtcdMixin, LoggerMixin):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def url(self, path):
        return urljoin(f'http://{self.host}:{self.port}', path)

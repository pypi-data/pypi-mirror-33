import os
import sys
import logging

from logging import handlers
from functools import wraps


def get_logger(name="root"):
    return Logger(name)


class Logger(object):
    """
    logger的实现
    """
    format_string = "{asctime} {level} {logger}:" \
                    " env: {env}, user: {user}, {message}"

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.propagate = False
        self.json = False
        if os.getenv("LOG_FILE") in ["true", "True", "1"]:
            dictionary = os.getenv("LOG_DIR", "/tmp")
            filename = os.getenv("LOG_FILENAME", "test.log")
            os.makedirs(dictionary, exist_ok=True)
            file_handler = handlers.RotatingFileHandler(
                os.path.join(dictionary, filename),
                maxBytes=10*1024*1024,
                backupCount=7)
            self.set_handler(file_handler)
        else:
            self.set_handler(logging.StreamHandler(sys.stdout))
        self.user = None

    def set_handler(self, handler):
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(self._get_formatter())
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def __getattr__(self, item):
        if item.upper() in logging._nameToLevel:
            func = getattr(self.logger, item)

            @wraps(func)
            def wrapper(*args, **kwargs):
                extra = kwargs.pop("extra", {})
                extra.setdefault("level", item.upper())
                extra.setdefault('env', os.getenv("PAAS_TARGET", "")),
                extra.setdefault('user', getattr(self.user, "name", None)),
                extra.setdefault("logger", self.name)
                kwargs["extra"] = extra
                return func(*args, **kwargs)
            return wrapper

        raise AttributeError

    def _get_formatter(self):
        if self.json:
            # 目前没有安装此依赖
            from pythonjsonlogger import jsonlogger
            return jsonlogger.JsonFormatter()
        else:
            return logging.Formatter(self.format_string, style="{")
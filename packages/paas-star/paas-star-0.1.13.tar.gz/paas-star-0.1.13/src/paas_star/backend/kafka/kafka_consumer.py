import asyncio

from functools import partial
from kafka import KafkaConsumer as _KC


class KafkaConsumer(_KC):
    callback = None

    def _consume(self):
        try:
            return self.__next__()
        except StopIteration as e:
            return None

    async def consume(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._consume)

    @classmethod
    def from_etcd(cls, callback=None):
        cls.callback = cls.callback or callback
        return partial(cls,
                       bootstrap_servers=callback(),
                       consumer_timeout_ms=1000)
import asyncio

from functools import partial
from kafka import KafkaProducer as _KP


class KafkaProducer(_KP):
    callback = None

    def produce_callback(self, waiter, value):
        waiter.set_result(value)

    def produce_errback(self, waiter, value):
        waiter.set_result(value)

    async def produce(self, topic, message):
        loop = asyncio.get_event_loop()
        waiter = loop.create_future()
        future = super(KafkaProducer, self).send(topic, message.encode())
        future.add_callback(self.produce_callback, waiter)
        future.add_errback(self.produce_errback, waiter)
        await waiter
        return future.get()

    @classmethod
    def from_etcd(cls, callback=None):
        cls.callback = cls.callback or callback
        return partial(cls,
                       bootstrap_servers=callback(),
                       retries=3)

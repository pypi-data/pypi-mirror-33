import typing

from functools import partial
from archsdk import get_service
from star_builder import Component

from .. import Manager
from .kafka_consumer import KafkaConsumer
from .kafka_producer import KafkaProducer

SERVICE = "kafka"
KafkaConsumerManger = typing.NewType("KafkaConsumerManger", Manager)
KafkaProducerManger = typing.NewType("KafkaProducerManger", Manager)


class CallbackMixin(object):

    def callback(self):
        return [c["host"] + ":" + str(c["port"]) for c in get_service(SERVICE)]


class KafkaConsumerComponent(Component, CallbackMixin):

    def resolve(self) -> KafkaConsumer:
        client_warpper = partial(
            KafkaConsumer,
            bootstrap_servers=self.callback(),
            consumer_timeout_ms=1000)
        return client_warpper


class KafkaProducerComponent(Component, CallbackMixin):

    def resolve(self) -> KafkaProducer:
        return KafkaProducer(bootstrap_servers=self.callback(), retries=3)


class KafkaConsumerManagerComponent(Component, CallbackMixin):

    def resolve(self) -> KafkaConsumerManger:
        return KafkaConsumerManger(
            Manager(partial(KafkaConsumer.from_etcd, callback=self.callback)))


class KafkaProducerManagerComponent(Component, CallbackMixin):

    def resolve(self) -> KafkaProducerManger:
        return KafkaProducerManger(
            Manager(partial(KafkaConsumer.from_etcd, callback=self.callback)))

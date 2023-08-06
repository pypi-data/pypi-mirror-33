import typing

from functools import partial
from archsdk import get_service
from star_builder import Component

from .. import Manager
from .kafka_consumer import KafkaConsumer
from .kafka_producer import KafkaProducer


KafkaConsumerManger = typing.NewType("KafkaConsumerManger", Manager)
KafkaProducerManger = typing.NewType("KafkaProducerManger", Manager)


class KafkaConsumerComponent(Component):

    def resolve(self) -> KafkaConsumer:

        client_warpper = partial(
            KafkaConsumer,
            bootstrap_servers=[c["host"] + ":" + str(c["port"])
                               for c in get_service("kafka")],
            consumer_timeout_ms=1000)
        return client_warpper


class KafkaProducerComponent(Component):

    def resolve(self) -> KafkaProducer:

        return KafkaProducer(
            bootstrap_servers=[c["host"] + ":" + str(c["port"])
                               for c in get_service("kafka")],
            retries=3)


class KafkaConsumerManagerComponent(Component):

    def callback(self):
        return [c["host"] + ":" + str(c["port"]) for c in get_service("kafka")]

    def resolve(self) -> KafkaConsumerManger:
        return KafkaConsumerManger(
            Manager(partial(KafkaConsumer.from_etcd, callback=self.callback)))


class KafkaProducerManagerComponent(Component):

    def callback(self):
        return [c["host"] + ":" + str(c["port"]) for c in get_service("kafka")]

    def resolve(self) -> KafkaProducerManger:
        return KafkaProducerManger(
            Manager(partial(KafkaConsumer.from_etcd, callback=self.callback)))

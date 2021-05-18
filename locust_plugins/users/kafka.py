import time
from confluent_kafka import Producer
from locust import User
import functools


class KafkaUser(User):
    abstract = True
    # overload these values in your subclass
    bootstrap_servers: str = None  # type: ignore

    def __init__(self, environment):
        super().__init__(environment)
        self.client: KafkaClient = KafkaClient(environment=environment, bootstrap_servers=self.bootstrap_servers)

    def on_stop(self):
        self.client.producer.flush(5)


def _on_delivery(environment, identifier, response_length, start_time, context, err, _msg):
    environment.events.request.fire(
        request_type="ENQUEUE",
        name=identifier,
        response_time=(time.monotonic() - start_time) * 1000,
        response_length=response_length,
        context=context,
        exception=err,
    )


class KafkaClient:
    def __init__(self, *, environment, bootstrap_servers):
        self.environment = environment
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def send(self, topic: str, value: bytes, key=None, response_length_override=None, name=None, context={}):
        start_time = time.monotonic()
        identifier = name if name else topic
        response_length = response_length_override if response_length_override else len(value)
        callback = functools.partial(_on_delivery, self.environment, identifier, response_length, start_time, context)
        self.producer.produce(topic, value, key, on_delivery=callback)
        response_length = response_length_override if response_length_override else len(value)

        self.producer.poll()

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


def _on_delivery(environment, topic, response_length, start_time, err, _msg):
    if err:
        environment.events.request_failure.fire(
            request_type="ENQUEUE",
            name=topic,
            response_time=int((time.monotonic() - start_time) * 1000),
            response_length=response_length,
            exception=err,
        )
    else:
        environment.events.request_success.fire(
            request_type="ENQUEUE",
            name=topic,
            response_time=int((time.monotonic() - start_time) * 1000),
            response_length=response_length,
        )


class KafkaClient:
    def __init__(self, *, environment, bootstrap_servers):
        self.environment = environment
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def send(self, topic: str, value: bytes, key=None, response_length_override=None):
        start_time = time.monotonic()
        response_length = response_length_override if response_length_override else len(value)
        callback = functools.partial(_on_delivery, self.environment, topic, response_length, start_time)
        self.producer.produce(topic, value, key, on_delivery=callback)
        response_length = response_length_override if response_length_override else len(value)

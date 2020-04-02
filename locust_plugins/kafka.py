# inspired by https://medium.com/locust-io-experiments/locust-experiments-locust-meets-kafka-b9d9e6e49537
import time
from kafka import KafkaProducer
from locust import Locust


class KafkaLocust(Locust):
    # overload these values in your subclass
    bootstrap_servers = None
    value_serializer = str.encode

    def __init__(self, environment):
        super().__init__(environment)
        self.client = KafkaClient(
            environment, bootstrap_servers=type(self).bootstrap_servers, value_serializer=type(self).value_serializer
        )

    def teardown(self):
        # this should actually be run for every locust instead of just once, but it is better than nothing...
        self.client.producer.flush(timeout=5)


class KafkaClient:
    def __init__(self, environment, bootstrap_servers, value_serializer):
        self.environment = environment
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=value_serializer)

    def send(self, topic, key=None, message=None):
        start_time = time.time()
        future = self.producer.send(topic, key=key, value=message)
        future.add_callback(self.__handle_success, start_time)
        future.add_errback(self.__handle_failure, start_time, topic)

    def __handle_success(self, start_time, record_metadata):
        self.environment.events.request_success.fire(
            request_type="ENQUEUE",
            name=record_metadata.topic,
            response_time=int((time.time() - start_time) * 1000),
            response_length=record_metadata.serialized_value_size,
        )

    def __handle_failure(self, exception, start_time, topic):
        self.environment.events.request_failure.fire(
            request_type="ENQUEUE",
            name=topic,
            response_time=int((time.time() - start_time) * 1000),
            exception=exception,
        )

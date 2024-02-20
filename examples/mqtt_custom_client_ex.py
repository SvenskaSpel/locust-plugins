import os
import ssl
import time
import typing

from locust import task, TaskSet
from locust.env import Environment
from locust.user.wait_time import between
from locust_plugins.users.mqtt import MqttUser
from locust_plugins.users.mqtt import MqttClient



tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
tls_context.load_verify_locations(os.environ["LOCUST_MQTT_CAFILE"])

# extend the MqttClient class with your own custom implementation
class MyMqttClient(MqttClient):
    def __init__(
        self,
        *args,
        environment: Environment,
        client_id: typing.Optional[str] = None,
        **kwargs,
    ):
        super().__init__(*args, environment, client_id, **kwargs)

    # you can override the event name with your custom implementation
    def _generate_event_name(self, event_type: str, qos: int, topic: str):
        return f"mqtt:{event_type}:{qos}"


class MyUser(MqttUser):
    # override the client_cls with your custom MqttClient implementation
    client_cls: typing.Type[MyMqttClient] = MyMqttClient

    @task
    class MyTasks(TaskSet):
        # Sleep for a while to allow the client time to connect.
        # This is probably not the most "correct" way to do this: a better method
        # might be to add a gevent.event.Event to the MqttClient's on_connect
        # callback and wait for that (with a timeout) here.
        # However, this works well enough for the sake of an example.
        def on_start(self):
            time.sleep(5)

        @task
        def say_hello(self):
            self.client.publish("hello/locust", b"hello world")

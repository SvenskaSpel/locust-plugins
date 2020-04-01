from locust_plugins.utils import run_single_user
from locust_plugins.kafka import KafkaLocust
from locust import task
from locust.wait_time import constant
import time
import random
import os


class MyLocust(KafkaLocust):
    bootstrap_servers = os.environ["LOCUST_KAFKA_SERVERS"].split(",")

    @task
    def t(self):
        self.client.send("lafp_test", message=f"{time.time() * 1000}:" + ("kafka" * 24)[: random.randint(32, 128)])
        self.client.producer.flush(timeout=5)
        time.sleep(1)

    wait_time = constant(0)


if __name__ == "__main__":
    run_single_user(MyLocust)

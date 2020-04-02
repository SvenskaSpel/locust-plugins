from locust_plugins.debug import run_single_user
from locust_plugins.kafka import KafkaLocust
from locust import task, TaskSet
from locust.wait_time import constant
import time
import random
import os


class MyTaskSet(TaskSet):
    @task
    def t(self):
        self.client.send("lafp_test", message=f"{time.time() * 1000}:" + ("kafka" * 24)[: random.randint(32, 128)])
        self.client.producer.flush(timeout=5)
        time.sleep(1)


class MyLocust(KafkaLocust):
    bootstrap_servers = os.environ["LOCUST_KAFKA_SERVERS"].split(",")
    tasks = {MyTaskSet: 1}
    task_set = MyTaskSet
    wait_time = constant(0)


if __name__ == "__main__":
    run_single_user(MyLocust)

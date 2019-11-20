from locust_plugins.listeners import TimescaleListener
from locust import HttpLocust, TaskSet, task
from locust.wait_time import constant

TimescaleListener("example", "env1")


class MyTaskSet(TaskSet):
    @task
    def index(self):
        self.client.post("/authentication/1.0/getResults", {"username": "something"})


class MyHttpLocust(HttpLocust):
    task_set = MyTaskSet
    wait_time = constant(1)
    host = "http://example.com"

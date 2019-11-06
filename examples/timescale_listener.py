from locust_plugins.listeners import TimescaleListener
from locust import HttpLocust, TaskSet, task

TimescaleListener("example", "testenv1")


class MyTaskSet(TaskSet):
    @task
    def index(self):
        self.client.post("/authentication/1.0/getResults", {"username": "something"})


class MyHttpLocust(HttpLocust):
    task_set = MyTaskSet
    min_wait = 100
    max_wait = 100
    host = "http://example.com"

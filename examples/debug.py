# How to use VS Code debugger with Locust
from locust_plugins.utils import run_single_user
from locust import task, TaskSet, HttpLocust, env
from locust.wait_time import constant


class MyTask(TaskSet):
    @task
    def task1(self):
        self.client.get("/1")

    @task
    def task2(self):
        self.client.get("/2")


class SimpleHttpLocust(HttpLocust):
    task_set = MyTask
    wait_time = constant(0)


# allow running as executable, to support attaching the debugger
if __name__ == "__main__":
    SimpleHttpLocust.host = "http://example.com"
    run_single_user(SimpleHttpLocust)

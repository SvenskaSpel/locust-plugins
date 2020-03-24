# How to use VS Code debugger with Locust
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()
from locust_plugins.listeners import PrintListener
from locust import task, TaskSet, HttpLocust, env, Events
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
    env = env.Environment()
    PrintListener(env)
    SimpleHttpLocust.wait_time = constant(0)
    SimpleHttpLocust._catch_exceptions = False
    SimpleHttpLocust.host = "http://example.com"
    SimpleHttpLocust(env).run()

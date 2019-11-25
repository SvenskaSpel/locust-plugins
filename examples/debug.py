# How to use VS Code debugger with Locust
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()
from locust_plugins.listeners import PrintListener
from locust import task, TaskSet
from locust.wait_time import constant
from locust.contrib.fasthttp import FastHttpLocust


class UserBehavior(TaskSet):
    @task
    def my_task(self):
        self.client.get("/")


class MyHttpLocust(FastHttpLocust):
    task_set = UserBehavior
    wait_time = constant(1)
    if __name__ == "__main__":
        host = "https://www.example.com"


# allow running as executable, to support attaching the debugger
if __name__ == "__main__":
    PrintListener()
    MyHttpLocust._catch_exceptions = False
    MyHttpLocust().run()

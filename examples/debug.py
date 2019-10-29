# How to use VS Code debugger with Locust
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()
from locust_plugins.listeners import PrintListener
from locust import HttpLocust, task, TaskSet


class UserBehavior(TaskSet):
    @task
    def my_task(self):
        self.client.post("/authentication/1.0/getResults", {"username": "something"})


class MyHttpLocust(HttpLocust):
    task_set = UserBehavior
    min_wait = 0
    max_wait = 0


# allow running as executable, mainly to support attaching the debugger
if __name__ == "__main__":
    PrintListener()
    MyHttpLocust._catch_exceptions = False
    MyHttpLocust().run()

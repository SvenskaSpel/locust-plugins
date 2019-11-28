# How to use VS Code debugger with Locust
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()
import locust_plugins.listeners
from locust import task, TaskSet, HttpLocust
from locust.wait_time import constant

locust_plugins.listeners.PrintListener()
# this needs to be registered after other listeners, because it will throw an exception if there is a failure
locust_plugins.listeners.RescheduleTaskOnFailListener()


class UserBehavior(TaskSet):
    @task
    def my_task(self):
        self.client.get("/fail")
        self.client.get("/this_will_never_be_run")


class MyHttpLocust(HttpLocust):
    task_set = UserBehavior
    wait_time = constant(1)
    if __name__ == "__main__":
        host = "https://www.example.com"


# allow running as executable, to support attaching the debugger
if __name__ == "__main__":
    MyHttpLocust._catch_exceptions = False
    MyHttpLocust().run()

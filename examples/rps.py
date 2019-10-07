#!/usr/bin/env python3
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()
locust_plugins.utils.print_json_on_decode_fail()
from locust_plugins.listeners import PrintListener, TimescaleListener
from locust_plugins.tasksets import TaskSetRPS
from locust import HttpLocust, task
import os

TimescaleListener("rps_example")
rps = float(os.environ["LOCUST_RPS"])


class UserBehavior(TaskSetRPS):
    @task
    def my_task(self):
        self.rps_sleep(rps)
        self.client.post("/authentication/1.0/getResults", {"username": "something"})


class MyHttpLocust(HttpLocust):
    task_set = UserBehavior
    min_wait = 0
    max_wait = 0
    if __name__ == "__main__":
        _catch_exceptions = False


# allow running as executable, mainly to support attaching the debugger
if __name__ == "__main__":
    PrintListener()
    MyHttpLocust().run()

#!/usr/bin/env python3
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()

import os
from locust_plugins.mongoreader import MongoReader
from locust_plugins.listeners import PrintListener
from locust import HttpLocust, task, TaskSet
from locust.wait_time import constant

reader = MongoReader([{"env": os.environ["LOCUST_TEST_ENV"]}, {"tb": 0}, {"lb": 1}])


class UserBehavior(TaskSet):
    @task
    def my_task(self):
        with reader.customer() as customer:
            self.client.get(f"/?ssn={customer['ssn']}")


class MyHttpLocust(HttpLocust):
    task_set = UserBehavior
    wait_time = constant(0)
    host = "http://example.com"


# allow running as executable, to support attaching the debugger
if __name__ == "__main__":
    PrintListener()
    MyHttpLocust._catch_exceptions = False
    MyHttpLocust().run()

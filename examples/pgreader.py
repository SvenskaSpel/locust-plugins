#!/usr/bin/env python3
import os
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()
locust_plugins.utils.print_json_on_decode_fail()
from locust_plugins.listeners import PrintListener, TimescaleListener
from locust_plugins.readers import PostgresReader
from locust import HttpLocust, task, TaskSet

TimescaleListener("example")

customer_reader = PostgresReader(f"env='{os.environ['LOCUST_TEST_ENV']}' AND tb=0 and lb=1")


class UserBehavior(TaskSet):
    @task
    def my_task(self):
        customer = customer_reader.get()
        self.client.get(f"/?ssn={customer['ssn']}")
        customer_reader.release(customer)


class MyHttpLocust(HttpLocust):
    task_set = UserBehavior
    min_wait = 0
    max_wait = 0
    host = "http://example.com"
    if __name__ == "__main__":
        _catch_exceptions = False


# allow running as executable, mainly to support attaching the debugger
if __name__ == "__main__":
    PrintListener()
    MyHttpLocust().run()

#!/usr/bin/env python3
import os
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()
locust_plugins.utils.print_json_on_decode_fail()
from locust_plugins.listeners import PrintListener, TimescaleListener
from locust_plugins.readers import PostgresReader
from locust_plugins.tasksets import TaskSetRPS
from locust import HttpLocust, task

TimescaleListener("example")

CUSTOMER_READER = PostgresReader(os.environ["LOCUST_TEST_ENV"])
RPS = float(os.environ["LOCUST_RPS"])


class UserBehavior(TaskSetRPS):
    @task
    def my_task(self):
        self.rps_sleep(RPS)
        self.client.get("/")
        customer = CUSTOMER_READER.get()
        self.client.post("/", data={"ssn": customer["ssn"]})
        CUSTOMER_READER.release(customer)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 0
    max_wait = 0
    if __name__ == "__main__":
        host = "http://example.com"


# allow running as executable, mainly to support attaching the debugger
if __name__ == "__main__":
    PrintListener()
    WebsiteUser().run()

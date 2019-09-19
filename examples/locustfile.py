#!/usr/bin/env python3
import os
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()
locust_plugins.utils.print_json_on_decode_fail()
from locust_plugins.listeners import PrintListener, TimescaleListener
from locust_plugins.readers import PostgresReader
from locust_plugins.tasksets import TaskSetRPS
from locust import HttpLocust, task

locust_plugins.listeners.Timescale("example")

customer_reader = PostgresReader(os.environ["LOCUST_TEST_ENV"])
rps = float(os.environ["LOCUST_RPS"])


class UserBehavior(TaskSetRPS):
    @task
    def myTask(self):
        self.rps_sleep(rps)
        self.client.get("/")
        customer = customer_reader.get()
        self.client.post("/", data={"ssn": customer["ssn"]})
        customer_reader.release(customer)


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

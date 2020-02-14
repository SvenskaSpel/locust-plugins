#!/usr/bin/env python3
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()

import os
from locust_plugins.mongoreader import MongoReader
from locust_plugins.listeners import PrintListener
from locust import HttpLocust, task, TaskSet
from locust.wait_time import constant_pacing

reader = MongoReader(
    filters=[{"tb": 0}, {"lb": 1}],
    id_column="ssn",
    uri=os.environ["LOCUST_MONGO"],
    database=os.environ["LOCUST_MONGO_DATABASE"],
    collection=os.environ["LOCUST_MONGO_COLLECTION"],
)


class UserBehavior(TaskSet):
    @task
    def my_task(self):
        with reader.user() as user:
            self.client.get(f"/?ssn={user['ssn']}")


class MyHttpLocust(HttpLocust):
    task_set = UserBehavior
    wait_time = constant_pacing(1)
    host = "http://example.com"


# allow running as executable, to support attaching the debugger
if __name__ == "__main__":
    PrintListener()
    MyHttpLocust._catch_exceptions = False
    MyHttpLocust().run()

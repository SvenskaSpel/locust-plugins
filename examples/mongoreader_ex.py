#!/usr/bin/env python3
from locust_plugins.debug import run_single_user
import os
from locust_plugins.mongoreader import MongoReader
from locust import HttpUser, task

reader = MongoReader(
    filters=[{"tb": 0}, {"lb": 1}],
    id_column="ssn",
    uri=os.environ["LOCUST_MONGO"],
    database=os.environ["LOCUST_MONGO_DATABASE"],
    collection=os.environ["LOCUST_MONGO_COLLECTION"],
)


class MyUser(HttpUser):
    @task
    def my_task(self):
        with reader.user() as user:
            self.client.get(f"/?ssn={user['ssn']}")

    host = "http://example.com"


# allow running as executable, to support attaching the debugger
if __name__ == "__main__":
    run_single_user(MyUser)

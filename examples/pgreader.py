#!/usr/bin/env python3
import os
from locust_plugins.postgresreader import PostgresReader
from locust import HttpLocust, task, TaskSet
from locust.wait_time import constant

customer_reader = PostgresReader(f"env='{os.environ['LOCUST_TEST_ENV']}' AND tb=0 AND lb=1")


class UserBehavior(TaskSet):
    @task
    def my_task(self):
        customer = customer_reader.get()
        self.client.get(f"/?ssn={customer['ssn']}")
        customer_reader.release(customer)


class MyHttpLocust(HttpLocust):
    task_set = UserBehavior
    wait_time = constant(0)
    host = "http://example.com"

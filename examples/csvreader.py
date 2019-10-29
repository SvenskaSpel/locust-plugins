from locust_plugins.readers import CSVReader
from locust import HttpLocust, TaskSet, task

ssn_reader = CSVReader("ssn.csv")


class MyTaskSet(TaskSet):
    @task
    def index(self):
        customer = next(ssn_reader)
        self.client.get(f"/?ssn={customer[0]}")


class MyHttpLocust(HttpLocust):
    task_set = MyTaskSet
    min_wait = 100
    max_wait = 100
    host = "http://example.com"

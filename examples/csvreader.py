from locust_plugins.readers import CSVReader
from locust import TaskSet, HttpLocust, task
from locust.wait_time import constant

ssn_reader = CSVReader("ssn.csv")


class MyTaskSet(TaskSet):
    @task
    def index(self):
        customer = next(ssn_reader)
        self.client.get(f"/?ssn={customer[0]}")


class MyHttpLocust(HttpLocust):
    task_set = MyTaskSet
    wait_time = constant(0)
    host = "http://example.com"

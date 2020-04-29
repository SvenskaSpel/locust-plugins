from locust_plugins.csvreader import CSVReader
from locust import HttpUser, task
from locust.wait_time import constant

ssn_reader = CSVReader("ssn.csv")


class MyHttpUser(HttpUser):
    @task
    def index(self):
        customer = next(ssn_reader)
        self.client.get(f"/?ssn={customer[0]}")

    wait_time = constant(0)
    host = "http://example.com"

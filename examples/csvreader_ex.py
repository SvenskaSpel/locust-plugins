from locust_plugins.csvreader import CSVReader
from locust import HttpUser, task

ssn_reader = CSVReader("ssn.csv")


class MyUser(HttpUser):
    @task
    def index(self):
        customer = next(ssn_reader)
        self.client.get(f"/?ssn={customer[0]}")

    host = "http://example.com"

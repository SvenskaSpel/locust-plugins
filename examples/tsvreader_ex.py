from locust_plugins.csvreader import CSVDictReader
from locust import HttpUser, task

ssn_reader = CSVDictReader("ssn.tsv", delimiter="\t")


class MyUser(HttpUser):
    @task
    def index(self):
        customer = next(ssn_reader)
        self.client.get(f"/?ssn={customer['ssn']}&age={customer['age']}")

    host = "http://example.com"

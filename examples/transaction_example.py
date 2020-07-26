from locust import HttpUser, task, SequentialTaskSet
from locust_plugins.transaction_manager import TransactionManager


class ExampleSequentialTaskSet(SequentialTaskSet):
    def on_start(self):
        self.tm = TransactionManager()

    @task
    def home(self):
        self.tm.start_transaction("startup")
        self.client.get("/", name="01 /")

    @task
    def get_config_json(self):
        self.client.get("/config.json", name="02 /config.json")
        self.tm.end_transaction("startup")


class TranactionExample(HttpUser):
    host = "https://www.demoblaze.com"

    tasks = [ExampleSequentialTaskSet]

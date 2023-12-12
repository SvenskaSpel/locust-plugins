# this example is a little more complex than it needs to be, but I wanted to highlight
# that it is entirely possible to have multiple distributors at the same time

from typing import Dict, List
from locust_plugins.mongoreader import MongoLRUReader
from locust_plugins.csvreader import CSVDictReader, CSVReader
from locust_plugins.distributor import Distributor
from locust import HttpUser, task, run_single_user, events
from locust.runners import WorkerRunner

distributors = {}


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    ssn_reader = None
    product_reader = None
    if not isinstance(environment.runner, WorkerRunner):
        product_reader = CSVReader("products.csv")
        csv = True
        if csv:
            ssn_reader = CSVDictReader("ssn.tsv", delimiter="\t")
        else:
            ssn_reader = MongoLRUReader({"foo": "bar"}, "last_login")
        product_reader = CSVReader("products.csv")
    distributors["customers"] = Distributor(environment, ssn_reader, "customers")
    distributors["products"] = Distributor(environment, product_reader, "products")


class MyUser(HttpUser):
    host = "http://www.example.com"

    @task
    def my_task(self) -> None:
        customer: Dict = next(distributors["customers"])
        product: List[str] = next(distributors["products"])
        self.client.get(f"/?customer={customer['ssn']}&product={product[0]}")


if __name__ == "__main__":
    run_single_user(MyUser)

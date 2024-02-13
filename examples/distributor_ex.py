# this example is a little more complex than it needs to be, but I wanted to highlight
# that it is entirely possible to have multiple distributors at the same time

from typing import Dict, List
from locust_plugins.csvreader import CSVDictReader, CSVReader
from locust_plugins.distributor import Distributor
from locust import HttpUser, task, run_single_user, events
from locust.runners import WorkerRunner

distributors = {}


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    ssn_iterator = None
    product_iterator = None
    if not isinstance(environment.runner, WorkerRunner):
        product_iterator = CSVReader("products.csv")
        ssn_iterator = CSVDictReader("ssn.tsv", delimiter="\t")
        # other readers work equally well
        # ssn_reader = MongoLRUReader({"foo": "bar"}, "last_login")
    distributors["products"] = Distributor(environment, product_iterator, "products")
    distributors["customers"] = Distributor(environment, ssn_iterator, "customers")


class MyUser(HttpUser):
    host = "http://www.example.com"

    @task
    def my_task(self) -> None:
        product: List[str] = next(distributors["products"])
        customer: Dict = next(distributors["customers"])
        self.client.get(f"/?product={product[0]}&customer={customer['ssn']}")


if __name__ == "__main__":
    run_single_user(MyUser)

from typing import Iterator
from locust_plugins.mongoreader import MongoLRUReader
from locust_plugins.csvreader import CSVDictReader
from locust_plugins import synchronizer
from locust import HttpUser, task, run_single_user


reader: Iterator
csv = True
if csv:
    reader = CSVDictReader("ssn.tsv", delimiter="\t")
else:
    reader = MongoLRUReader({"env": "test", "tb": False, "lb": True}, "last_login")
synchronizer.register(reader)
# optionally replace this with lazy initalization of Reader to avoid unnecessarily doing it on workers:
# synchronizer.register(None, MongoLRUReader, {"env": "test", "tb": False, "lb": True}, "last_login")


class MyUser(HttpUser):
    host = "http://www.example.com"

    @task
    def my_task(self):
        customer = synchronizer.getdata(self)
        self.client.get(f"/?{customer['ssn']}")


if __name__ == "__main__":
    run_single_user(MyUser)

from locust_plugins.mongoreader import MongoLRUReader
from locust_plugins.csvreader import CSVDictReader
from locust_plugins import synchronizer
from locust import HttpUser, task, run_single_user, events
from locust.runners import WorkerRunner


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    reader = None
    if not isinstance(environment.runner, WorkerRunner):
        csv = True
        if csv:
            reader = CSVDictReader("ssn.tsv", delimiter="\t")
        else:
            reader = MongoLRUReader({"foo": "bar"}, "last_login")
    synchronizer.register(environment, reader)


class MyUser(HttpUser):
    host = "http://www.example.com"

    @task
    def my_task(self):
        customer = synchronizer.getdata(self)
        self.client.get(f"/?{customer['ssn']}")


if __name__ == "__main__":
    run_single_user(MyUser)

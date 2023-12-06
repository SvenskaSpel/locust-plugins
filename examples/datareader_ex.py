from locust_plugins.mongoreader import SimpleMongoReader

# from locust_plugins.csvreader import CSVDictReader
from locust_plugins.synchronizer import data_synchronizer, getdata
from locust import HttpUser, task, events, runners, run_single_user
import time


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    # ssn_reader = CSVDictReader("ssn.tsv", delimiter="\t")
    ssn_reader = SimpleMongoReader({"env": "test", "tb": False, "lb": True}, "last_login")
    data_synchronizer(ssn_reader)


class MyUser(HttpUser):
    @task
    def my_task(self):
        start_time = time.time()
        start_perf_counter = time.perf_counter()
        user = getdata(self)
        self.environment.events.request.fire(
            request_type="fake",
            # name=user["ssn"],
            name="fake",
            start_time=start_time,
            response_time=(time.perf_counter() - start_perf_counter) * 1000,
            response_length=0,
            context={**self.context()},
            exception=None,
        )

    host = "http://localhost:8089"


if __name__ == "__main__":
    run_single_user(MyUser)

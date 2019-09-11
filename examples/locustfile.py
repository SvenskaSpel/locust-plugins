if __name__ == "__main__":
    from locust_extensions import enable_gevent_debugging

    enable_gevent_debugging.setup_ptvsd()

from locust_extensions import reporter, customer_reader, task_sets
from locust_extensions import print_json_on_fail  # pylint: disable=unused-import
from locust import HttpLocust, task
import os

reporter.Reporter("example")

rps = float(os.environ["LOCUST_RPS"])

cr = customer_reader.CustomerReader("itp2")


class UserBehavior(task_sets.TaskSetRPS):
    def on_start(self):
        self.client.verify = False  # disable ssl validation

    @task
    def get_results(self):
        self.rps_sleep(rps)
        customer = cr.get()
        self.client.post("/", data={"ssn": customer["ssn"]})
        cr.release(customer)
        if __name__ == "__main__":
            print("iteration complete!")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 0
    max_wait = 0
    if __name__ == "__main__":
        host = "http://example.com"


# allow running as executable for debugging
if __name__ == "__main__":
    x = WebsiteUser()
    x.run()

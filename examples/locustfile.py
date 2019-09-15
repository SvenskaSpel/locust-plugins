import locust_plugins.utils

if __name__ == "__main__":
    locust_plugins.utils.setup_ptvsd()

locust_plugins.utils.print_json_on_fail()

import locust_plugins.readers
import locust_plugins.tasksets
import locust_plugins.listeners

from locust import HttpLocust, task
import os

locust_plugins.listeners.Timescale("example")

rps = float(os.environ["LOCUST_RPS"])

customer_reader = locust_plugins.readers.PostgresReader(os.environ["TEST_ENV"])


class UserBehavior(locust_plugins.tasksets.TaskSetRPS):
    def on_start(self):
        self.client.verify = False  # disable ssl validation

    @task
    def get_results(self):
        self.rps_sleep(rps)
        customer = customer_reader.get()
        self.client.post("/", data={"ssn": customer["ssn"]})
        customer_reader.release(customer)
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

# a more in-depth example of how to use run_single_user in combination with init method, and then stop the test immediately
from locust import task, HttpUser, events
from locust.exception import StopUser
from locust_plugins import run_single_user
from locust_plugins import listeners
import time


class MyUser(HttpUser):
    @task
    def t(self):
        self.client.post("/")
        time.sleep(2)
        self.client.post("/")
        raise StopUser()


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    listeners.Timescale(environment)


if __name__ == "__main__":
    MyUser.host = "http://example.com"
    run_single_user(MyUser, include_time=True, include_length=True)

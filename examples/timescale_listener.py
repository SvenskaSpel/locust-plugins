from locust_plugins.listeners import TimescaleListener
from locust import HttpUser, task, events
from locust.wait_time import constant


class MyHttpUser(HttpUser):
    @task
    def index(self):
        self.client.post("/authentication/1.0/getResults", {"username": "something"})

    wait_time = constant(1)
    host = "http://example.com"


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    TimescaleListener(env=environment, testplan="racing", target_env="myTestEnv")

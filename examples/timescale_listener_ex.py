from locust_plugins.listeners import TimescaleListener
from locust import HttpUser, task, events


class MyHttpUser(HttpUser):
    @task
    def index(self):
        self.client.post("/authentication/1.0/getResults", {"username": "something"})

    host = "http://example.com"


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    TimescaleListener(env=environment, testplan="racing", target_env="myTestEnv")

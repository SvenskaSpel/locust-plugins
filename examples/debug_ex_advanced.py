# a more in-depth example of how to use run_single_user in combination with init method
from locust import task, HttpUser, events
from locust_plugins import run_single_user
from locust_plugins.listeners import TimescaleListener


class MyUser(HttpUser):
    @task
    def t(self):
        self.client.post("/")


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    TimescaleListener(environment, "debug")


if __name__ == "__main__":
    MyUser.host = "http://example.com"
    run_single_user(MyUser, include_time=True, include_length=True, init_listener=on_locust_init)

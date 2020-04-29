from locust import HttpUser, task, events
from locust_plugins.debug import run_single_user
from locust_plugins.wait_time import constant_total_ips
from locust_plugins.listeners import TimescaleListener


class MyHttpUser(HttpUser):
    @task
    def my_task(self):
        self.client.get("/")

    wait_time = constant_total_ips(5)
    host = "https://www.example.com"


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    TimescaleListener(env=environment, testplan="racing", target_env="myTestEnv")


if __name__ == "__main__":
    run_single_user(MyHttpUser)

from locust import HttpUser, task, events
from locust_plugins import run_single_user, constant_total_ips
from locust_plugins.listeners import TimescaleListener


class MyUser(HttpUser):
    @task
    def my_task(self):
        self.client.get("/")

    wait_time = constant_total_ips(5)
    host = "https://www.example.com"


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    TimescaleListener(env=environment, testplan="constant_total_ips", target_env="myTestEnv")


if __name__ == "__main__":
    run_single_user(MyUser)

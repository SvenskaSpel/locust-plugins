from locust import HttpUser, task
from locust_plugins import run_single_user, constant_total_ips


class MyUser(HttpUser):
    wait_time = constant_total_ips(2)

    @task
    def my_task(self):
        self.client.get("/")

    host = "https://www.example.com"


if __name__ == "__main__":
    run_single_user(MyUser, include_time=True)

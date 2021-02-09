# this will run approximately 5 iterations per second, regardless of the number of users or response times
# (assuming response times are low enough / user count is high enough to make that throughput possible)

from locust import HttpUser, task
from locust_plugins import constant_total_ips


class MyUser(HttpUser):
    wait_time = constant_total_ips(5)

    @task
    def t(self):
        self.client.get("/1")
        self.client.get("/2")
        # because we do two requests in each iteration, the total request rate will be ~10/s

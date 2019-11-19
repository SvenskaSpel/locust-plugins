from locust_plugins.tasksets import TaskSetRPS
from locust import task
from locust.wait_time import constant
from locust.contrib.fasthttp import FastHttpLocust


class UserBehavior(TaskSetRPS):
    @task
    def my_task(self):
        self.rps_sleep(2)
        self.client.post("/authentication/1.0/getResults", {"username": "something"})


class MyHttpLocust(FastHttpLocust):
    task_set = UserBehavior
    wait_time = constant(0)

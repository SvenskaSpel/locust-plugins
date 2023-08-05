from locust import HttpUser, task, events
from locust_plugins.listeners import jmeter


class DemoBlazeUser(HttpUser):
    host = "https://www.demoblaze.com"

    @task
    def t(self):
        self.client.get("/")


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    jmeter.JmeterListener(env=environment, testplan="examplePlan")

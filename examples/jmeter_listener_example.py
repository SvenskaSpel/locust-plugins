from locust import HttpUser, task, events
from locust_plugins import jmeter_listener


class DemoBlazeUser(HttpUser):
    host = "https://www.demoblaze.com"

    @task
    def t(self):
        self.client.get("/")


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    jmeter_listener.JmeterListener(env=environment, testplan="examplePlan")

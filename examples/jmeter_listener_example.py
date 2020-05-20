from locust import HttpUser, task, events
from locust_plugins.jmeter_listener import JmeterListener


class DemoBlazeUser(HttpUser):
    host = "https://www.demoblaze.com"

    @task
    def t(self):
        self.client.get("/")


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    JmeterListener(env=environment, testplan="examplePlan")

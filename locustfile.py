import sys
sys.path.append("./locust_plugins")

from locust_plugins.listeners import ApplicationInsightsListener
from locust import HttpUser, task, events, between

class MyHttpUser(HttpUser):
    @task
    def index(self):
        self.client.get("/Guilhermeslucas/resume")

    host = "https://github.com"
    wait_time = between(4, 10)


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    ApplicationInsightsListener(env=environment, instrumentation_key="ba987502-d556-429d-9072-c5a8d59f9027")
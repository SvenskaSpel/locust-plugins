from locust import HttpUser, SequentialTaskSet, task, between, events
from locust_plugins.jmeter_listener import JmeterListener

import json, random, string

class DemoBlazeUser(HttpUser):
    host = "https://www.demoblaze.com"
    wait_time = between(2, 5)

    @task
    def home(self):
        self.client.get("/", name ="01 /")

    @task
    def get_config_json(self):
        response = self.client.get("/config.json", name="02 /config.json")
        response_json = json.loads(response.text)
        self.api_host = response_json["API_URL"]

@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    JmeterListener(env=environment, testplan="examplePlan")

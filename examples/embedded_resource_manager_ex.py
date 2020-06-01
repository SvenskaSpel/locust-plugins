import sys, os
sys.path.append(os.getcwd())
from locust_plugins.embedded_resource_manager import HttpUserWithResources
from locust import task, events
import time

class TestUserWithResources(HttpUserWithResources):
    bundle_resource_stats=False
    default_resource_filter=".*[^(js)]$"
    @task
    def include_resources_true(self):
        response = self.client.get("/", resource_filter=".*[^(js)]$")

    @task
    def include_resources_missing(self):
        response = self.client.get("/cart.html")

    @task
    def include_resources_false(self):
        response = self.client.get("/index.html", include_resources=False)
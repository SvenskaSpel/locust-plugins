from locust_plugins.users import HttpUserWithResources
from locust import task


class TestUserWithResources(HttpUserWithResources):
    # these values can be overridden
    # bundle_resource_stats=False
    # default_resource_filter=".*[^(js)]$"
    @task
    def include_resources_default(self):
        self.client.get("/cart.html")

    @task
    def include_resources_true(self):
        self.client.get("/", resource_filter=".*[^(js)]$")

    @task
    def include_resources_false(self):
        self.client.get("/index.html", include_resources=False)

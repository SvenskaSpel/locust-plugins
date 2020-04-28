# How to use VS Code debugger with Locust
from locust_plugins.debug import run_single_user
from locust import task, HttpLocust, constant


class SimpleHttpLocust(HttpLocust):
    @task
    def t(self):
        self.client.get("/")

    wait_time = constant(0)


# when executed as a script, run a single locust in a way suitable for the vs code debugger
if __name__ == "__main__":
    SimpleHttpLocust.host = "http://example.com"
    run_single_user(SimpleHttpLocust)

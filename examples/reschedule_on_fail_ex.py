# How to use VS Code debugger with Locust
from locust_plugins import run_single_user
import locust_plugins.listeners
from locust import task, HttpUser, events


class MyUser(HttpUser):
    host = "http://example.com"

    @task
    def my_task(self):
        self.client.get("/fail")
        print("this will never be run")


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    # make sure this is the last event handler you register, as later ones will not be triggered
    # if there is a failure
    locust_plugins.listeners.RescheduleTaskOnFailListener(environment)


if __name__ == "__main__":
    run_single_user(MyUser, init_listener=on_locust_init)

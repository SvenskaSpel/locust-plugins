# How to use VS Code debugger with Locust
import locust_plugins.listeners
from locust import task, HttpUser, events, run_single_user


class MyUser(HttpUser):
    host = "http://example.com"

    @task
    def my_task(self):
        self.client.get("/fail")
        print("this will never be run")


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    # make sure this is the last request event handler you register, as later ones will not get triggered
    # if there is a failure
    locust_plugins.listeners.RescheduleTaskOnFail(environment)


if __name__ == "__main__":
    run_single_user(MyUser)

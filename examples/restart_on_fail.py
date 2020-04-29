# How to use VS Code debugger with Locust
from locust_plugins.debug import run_single_user
import locust_plugins.listeners
from locust import task, HttpUser, events, env
from locust.wait_time import constant


class MyHttpUser(HttpUser):
    wait_time = constant(1)
    host = "http://example.com"

    @task
    def my_task(self):
        self.client.get("/fail")
        print("this will never be run")


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    locust_plugins.listeners.RescheduleTaskOnFailListener(environment)


if __name__ == "__main__":
    env = env.Environment()
    on_locust_init(env)
    run_single_user(MyHttpUser, env)

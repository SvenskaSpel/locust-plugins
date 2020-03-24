from locust_plugins.listeners import TimescaleListener
from locust import HttpLocust, TaskSet, task, events, env
from locust.wait_time import constant


class MyTaskSet(TaskSet):
    @task
    def index(self):
        self.client.post("/authentication/1.0/getResults", {"username": "something"})


class MyHttpLocust(HttpLocust):
    task_set = MyTaskSet
    wait_time = constant(1)
    host = "http://example.com"


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    TimescaleListener(env=environment, testplan="racing", target_env="myTestEnv")


if __name__ == "__main__":
    env = env.Environment()
    on_locust_init(env)
    MyHttpLocust._catch_exceptions = False
    MyHttpLocust(env).run()

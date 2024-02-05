import gevent
from locust import events
from locust import HttpUser, task, between
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
from locust_plugins.listeners.cloudwatch import CloudwatchAdapter
from unittest import TestCase


setup_logging("INFO", None)


class CloudwatchMock:
    def __init__(self):
        self.call_count = 0
        self.metrics_dict = {}

    def put_metric_data(self, Namespace, MetricData):
        self.call_count += 1
        self.metrics_dict[Namespace] = MetricData


cw = CloudwatchMock()


def on_locust_init(environment, **_kwargs):
    CloudwatchAdapter(environment, "MyExampleService", "perf", cw)


class User(HttpUser):
    wait_time = between(1, 3)
    host = "https://docs.locust.io"

    @task
    def my_task(self):
        self.client.get("/")


class TestCloudwatch(TestCase):
    def test_basic_flow(self):
        # setup Environment and Runner
        env = Environment(user_classes=[User], events=events)
        env.events.init.add_listener(on_locust_init)
        runner = env.create_local_runner()
        env.events.init.fire(environment=env, runner=runner)

        # start a greenlet that periodically outputs the current stats
        gevent.spawn(stats_printer(env.stats))

        # start a greenlet that save current stats to history
        gevent.spawn(stats_history, env.runner)
        env.runner.start(1, spawn_rate=10)

        # in 10 seconds stop the runner
        gevent.spawn_later(10, lambda: env.runner.quit())

        env.runner.greenlet.join()
        self.assertTrue(cw.call_count == 1)

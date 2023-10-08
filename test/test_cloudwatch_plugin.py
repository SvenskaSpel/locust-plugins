import gevent
from locust import events
from locust import HttpUser, task, between
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
from locust_plugins.listeners.cloudwatch import CloudwatchAdapter, ServiceContext
from locust_plugins import missing_extra
import logging

try:
    from moto import mock_cloudwatch
except ModuleNotFoundError:
    missing_extra("moto", "moto")

try:
    import boto3
except ModuleNotFoundError:
    missing_extra("boto3", "boto3")

setup_logging("INFO", None)

def on_locust_init(environment, **_kwargs):
    cw = _cloudwatch()
    CloudwatchAdapter(cw, environment, _service_context())


def _cloudwatch():
    with mock_cloudwatch():
        logging.info("Going to initialize cloudwatch")
        cw = boto3.client("cloudwatch")
        yield cw


def _service_context():
    return ServiceContext("MyExampleService", "perf")

events.init.add_listener(on_locust_init)

class User(HttpUser):
    wait_time = between(1, 3)
    host = "https://docs.locust.io"

    @task
    def my_task(self):
        self.client.get("/")


# setup Environment and Runner
env = Environment(user_classes=[User], events=events)
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

from locust import events
from locust_plugins.listeners.cloudwatch import CloudwatchAdapter, ServiceContext


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    CloudwatchAdapter(environment, ServiceContext("MyExampleService", "perf"))

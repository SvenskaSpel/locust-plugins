import traceback
import logging
import sys
from locust import main, events
from locust_plugins.listeners.cloudwatch import CloudwatchAdapter, ServiceContext


try:
    import boto3
except ModuleNotFoundError:
    traceback.print_exc()
    logging.error("boto3 is not installed by default, you need to install it using 'pip install boto3'")
    sys.exit(1)


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    CloudwatchAdapter(_cloudwatch(), environment, _service_context())


def _cloudwatch():
    return boto3.client("cloudwatch")


def _service_context():
    return ServiceContext("MyExampleService", "perf")


if __name__ == "__main__":
    main.main()

import logging
import os
import locust.env
from opencensus.ext.azure.log_exporter import AzureLogHandler


class ApplicationInsights:
    def __init__(self, env: locust.env.Environment, testplan="", instrumentation_key="", propagate_logs=True):
        self.testplan = testplan or "appinsightstestplan"
        self.env = env
        self.logger = logging.getLogger(__name__)

        if instrumentation_key != "":
            formated_key = "InstrumentationKey=" + instrumentation_key
        else:
            formated_key = "InstrumentationKey=" + str(os.getenv("APP_INSIGHTS_INSTRUMENTATION_KEY"))

        self.logger.addHandler(AzureLogHandler(connection_string=formated_key))
        self.logger.propagate = propagate_logs

        env.events.request.add_listener(self.request)

    def request(self, request_type, name, response_time, response_length, exception, **_kwargs):
        if exception:
            custom_dimensions = self._create_custom_dimensions_dict(
                request_type, "Failure", response_time, response_length, name, exception
            )
            message_to_log = "Failure: {} {} Response time: {} Number of Threads: {} Exception: {}.".format(
                str(request_type), str(name), str(response_time), custom_dimensions["thread_count"], str(exception)
            )
            self.logger.error(message_to_log, extra={"custom_dimensions": custom_dimensions})
        else:
            custom_dimensions = self._create_custom_dimensions_dict(
                request_type, "Success", response_time, response_length, name
            )
            message_to_log = "Success: {} {} Response time: {} Number of Threads: {}.".format(
                str(request_type), str(name), str(response_time), custom_dimensions["thread_count"]
            )
            self.logger.info(message_to_log, extra={"custom_dimensions": custom_dimensions})

    def _create_custom_dimensions_dict(self, method, result, response_time, response_length, endpoint, exception=None):
        custom_dimensions = self._safe_return_runner_values()

        custom_dimensions["host"] = str(self.env.host)
        custom_dimensions["method"] = str(method)
        custom_dimensions["result"] = result
        custom_dimensions["response_time"] = response_time
        custom_dimensions["response_length"] = response_length
        custom_dimensions["endpoint"] = str(endpoint)
        custom_dimensions["testplan"] = str(self.testplan)
        custom_dimensions["exception"] = str(exception)

        return custom_dimensions

    def _safe_return_runner_values(self):
        runner_values = {}

        if self.env.runner is None:
            runner_values["thread_count"] = ""
            runner_values["target_user_count"] = ""
            runner_values["spawn_rate"] = ""
        else:
            runner_values["thread_count"] = str(self.env.runner.user_count)
            runner_values["target_user_count"] = str(self.env.runner.target_user_count)
            runner_values["spawn_rate"] = str(self.env.runner.spawn_rate)

        return runner_values


class ApplicationInsightsListener:
    def __init__(self, *args, **kwargs):
        raise Exception("All listeners have had their -Listener suffix removed, please update your code.")

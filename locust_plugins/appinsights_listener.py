import logging
import os
import locust.env
from opencensus.ext.azure.log_exporter import AzureLogHandler

class ApplicationInsightsListener:
    def __init__(self, env: locust.env.Environment, testplan="", instrumentation_key=""):
        self.testplan = testplan or "appinsightstestplan"
        self.env = env
        self.logger = logging.getLogger(__name__)

        if instrumentation_key != "":
            formated_key = 'InstrumentationKey=' + instrumentation_key
        else:
            formated_key = 'InstrumentationKey=' + os.environ('APP_INSIGHTS_INSTRUMENTATION_KEY')

        self.logger.addHandler(AzureLogHandler(connection_string=formated_key))

        env.events.request_success.add_listener(self.request_success)
        env.events.request_failure.add_listener(self.request_failure)

    def request_success(self, request_type, name, response_time, response_length, **_kwargs):
        custom_dimensions = {}

        custom_dimensions['method'] = str(request_type)
        custom_dimensions['result'] = 'Success'
        custom_dimensions['response_time'] = response_time
        custom_dimensions['response_length'] = response_length
        custom_dimensions['endpoint'] = str(name)
        custom_dimensions['testplan'] = str(self.testplan)
        custom_dimensions['thread_count'] = str(self.env.runner.user_count)
        custom_dimensions['host'] = str(self.env.host)
        custom_dimensions['target_user_count'] = str(self.env.runner.target_user_count)
        custom_dimensions['spawn_rate'] = str(self.env.runner.spawn_rate)

        message_to_log = "Success: {} {} Response time: {} Response Length: {}.".format(str(request_type),
                                                                                        str(name),
                                                                                        str(response_time),
                                                                                        str(response_length))
 
        self.logger.info(message_to_log, extra={'custom_dimensions': custom_dimensions})

    def request_failure(self, request_type, name, response_time, response_length, exception, **_kwargs):
        custom_dimensions = {}

        custom_dimensions['method'] = str(request_type)
        custom_dimensions['result'] = 'Fail'
        custom_dimensions['response_time'] = response_time
        custom_dimensions['response_length'] = response_length
        custom_dimensions['endpoint'] = str(name)
        custom_dimensions['testplan'] = str(self.testplan)
        custom_dimensions['thread_count'] = str(self.env.runner.user_count)
        custom_dimensions['host'] = str(self.env.host)
        custom_dimensions['target_user_count'] = str(self.env.runner.target_user_count)
        custom_dimensions['spawn_rate'] = str(self.env.runner.spawn_rate)
        custom_dimensions['exception'] = str(exception)

        message_to_log = "Fail: {} {} Response time: {} Response Length: {} Exception: {}.".format(str(request_type),
                                                                                                    str(name),
                                                                                                    str(response_time),
                                                                                                    str(response_length),
                                                                                                    str(exception))

        self.logger.error(message_to_log, extra={'custom_dimensions': custom_dimensions})
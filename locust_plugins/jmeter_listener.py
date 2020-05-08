"""
a listener to provide results from locust tests in a JMeter compatible format
and thereby smooth the transition for JMeter users
"""

from datetime import datetime
from time import time
from locust import web
from locust import events


class JmeterListener:
    """
    create an intance of the listener at the start of a test
    to create a JMeter style results file
    """

    # holds results until processed
    csv_results = []

    def __init__(
            self,
            field_delimiter=",",
            row_delimiter="\n",
            timestamp_format="%Y-%m-%d %H:%M:%S",
            flush_size=100,
    ):
        # default JMeter field and row delimiters
        self.field_delimiter = field_delimiter
        self.row_delimiter = row_delimiter
        # a timestamp format, others could be added...
        self.timestamp_format = timestamp_format
        # how many records should be held before flushing to disk
        self.flush_size = flush_size
        # results filename format
        self.results_timestamp_format = "%Y_%m_%d_%H_%M_%S"
        self.results_filename = (
            "results_"
            + datetime.fromtimestamp(time()).strftime(self.results_timestamp_format)
            + ".csv"
        )

        # fields set by default in jmeter
        self.csv_headers = [
            "timeStamp",
            "elapsed",
            "label",
            "responseCode",
            "responseMessage",
            "threadName",
            "dataType",
            "success",
            "failureMessage",
            "bytes",
            "sentBytes",
            "grpThreads",
            "allThreads",
            "Latency",
            "IdleTime",
            "Connect",
        ]
        self.results_file = self.create_results_log()
        events.request_success.add_listener(self.csv_success_handler)
        events.request_failure.add_listener(self.csv_request_failure)
        events.quitting.add_listener(self.write_final_log)
        events.init.add_listener(self.on_locust_init)

    def on_locust_init(self, environment, **kw):
        if environment.web_ui:
            @environment.web_ui.app.route("/csv_results.csv")
            def csv_results_page():
                """
                a different way of obtaining results rather than writing to disk
                to use it getting all results back, set the flush_size to
                a high enough figure that it will not flush
                """
                response = environment.web_ui.app.response_class(
                    response=self.field_delimiter.join(self.csv_headers)
                    + self.row_delimiter
                    + self.row_delimiter.join(self.csv_results),
                    status=200,
                    mimetype="text/csv",
                )
                return response

    def add_result(
            self,
            success,
            request_type,
            name,
            response_time,
            response_length,
            exception,
            **kw
    ):
        """
        adds a result
        """
        timestamp = datetime.fromtimestamp(time()).strftime(self.timestamp_format)
        response_message = "OK" if success == "true" else "KO"
        # check to see if the additional fields have been populated. If not, set to a default value
        status_code = kw["status_code"] if "status_code" in kw else "0"
        thread_name = kw["thread_name"] if "thread_name" in kw else "unnamed"
        data_type = kw["data_type"] if "data_type" in kw else "unknown"
        bytes_sent = kw["bytes_sent"] if "bytes_sent" in kw else "0"
        group_threads = kw["group_threads"] if "group_threads" in kw else "0"
        all_threads = kw["all_threads"] if "all_threads" in kw else "0"
        latency = kw["latency"] if "latency" in kw else "0"
        idle_time = kw["idle_time"] if "idle_time" in kw else "0"
        connect = kw["connect"] if "connect" in kw else "0"

        row = [
            timestamp,
            str(round(response_time)),
            name,
            status_code,
            response_message,
            thread_name,
            data_type,
            success,
            exception,
            str(response_length),
            bytes_sent,
            group_threads,
            all_threads,
            latency,
            idle_time,
            connect,
        ]
        if len(self.csv_results) >= self.flush_size:
            self.flush_to_log()
        self.csv_results.append(self.field_delimiter.join(row))

    def csv_success_handler(
            self, request_type, name, response_time, response_length, **kw
    ):
        """
        handler for successful request event
        """
        self.add_result(
            "true", request_type, name, response_time, response_length, "", **kw
        )

    def csv_request_failure(
            self, request_type, name, response_time, response_length, exception, **kw
    ):
        """
        handler for failed request event
        """
        self.add_result(
            "false",
            request_type,
            name,
            response_time,
            response_length,
            str(exception),
            **kw
        )

    def create_results_log(self):
        """
        creates a results log
        """
        results_file = open(self.results_filename, "w")
        results_file.write(
            self.field_delimiter.join(self.csv_headers) + self.row_delimiter
        )
        results_file.close()
        return results_file

    def flush_to_log(self):
        """
        flushes results to log file
        """
        self.results_file = open(self.results_filename, "a")
        self.results_file.write(
            self.row_delimiter.join(self.csv_results) + self.row_delimiter
        )
        self.results_file.close()
        self.csv_results = []

    def write_final_log(self):
        """
        performs final write to log file when test complete
        """
        self.results_file = open(self.results_filename, "a")
        self.results_file.write(
            self.row_delimiter.join(self.csv_results) + self.row_delimiter
        )
        self.results_file.close()

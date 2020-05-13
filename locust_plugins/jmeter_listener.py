"""
a listener to provide results from locust tests in a JMeter compatible format
and thereby allow JMeter users with existing reporting solutions to transition more easily
"""

from datetime import datetime
from time import time
from locust import events
import logging


class JmeterListener:
    """
    create an intance of the listener at the start of a test
    to create a JMeter style results file
    different formats can be chosen in initialisation
    (field_delimiter row_delimiter and timestamp_format)
    and the number of results to send to a log file at a time (flush_size)
    by default, it will automatically log results (auto_log=True)
    if you want to manually override the pass/fail outcome and write a custom-made result
    set auto_log to false in initialisation and for each task and call add_result
    with the values you want to record
    Manual logging has to be used FastHttpUser
    """

    # holds results until processed
    csv_results = []

    def __init__(
            self,
            field_delimiter=",",
            row_delimiter="\n",
            timestamp_format="%Y-%m-%d %H:%M:%S",
            flush_size=100,
            auto_log=True,
    ):
        # determine whether to auto log requests or do it manually
        self.auto_log = auto_log
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
            "results_" + datetime.fromtimestamp(time()).strftime(self.results_timestamp_format) + ".csv"
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
        self.results_file = self._create_results_log()
        self.user_count = 0
        self.user_name = ""
        events.quitting.add_listener(self._write_final_log)
        events.init.add_listener(self.on_locust_init)

    def on_locust_init(self, environment, **kwargs):
        self.env = environment
        user_classes = self.env.user_classes
        self.runner = self.env.runner

        if environment.web_ui:

            @environment.web_ui.app.route("/csv_results.csv")
            def csv_results_page():
                """
                a different way of obtaining results rather than writing to disk
                to use it getting all results back, set the flush_size to
                a high enough value that it will not flush during your test
                """
                response = environment.web_ui.app.response_class(
                    response=self.field_delimiter.join(self.csv_headers)
                    + self.row_delimiter
                    + self.row_delimiter.join(self.csv_results),
                    status=200,
                    mimetype="text/csv",
                )
                return response

    def _create_results_log(self):
        """
        creates a results log
        """
        results_file = open(self.results_filename, "w")
        results_file.write(self.field_delimiter.join(self.csv_headers) + self.row_delimiter)
        results_file.flush()
        return results_file

    def _flush_to_log(self):
        """
        flushes results to log file
        """
        self.results_file.write(self.row_delimiter.join(self.csv_results) + self.row_delimiter)
        self.results_file.flush()
        self.csv_results = []

    def _write_final_log(self):
        """
        performs final write to log file when test complete
        """
        self.results_file.write(self.row_delimiter.join(self.csv_results) + self.row_delimiter)
        self.results_file.close()

    def start_logging(self, user):
        self.user_count += 1
        self.user_name = user.__class__.__name__
        if self.auto_log:
            user.client.request = self._add_record(user.client.request)

    def _add_record(self, func):
        def wrapper(wrappedself, *args, **kwargs):
            """
            adds a result
            """
            timestamp = datetime.fromtimestamp(time()).strftime(self.timestamp_format)
            name = kwargs["name"] if "name" in kwargs else "unknown"
            response = func(wrappedself, *args, **kwargs)
            if hasattr(response, "_manual_result"):
                logging.info(
                    "Found manually controlled result in '"
                    + name
                    + "' Change to manual logging to set pass/fail correctly"
                )
            try:
                status_code = str(response.status_code)
                thread_name = self.user_name
                elapsed_time = str(round(response.elapsed.microseconds / 1000))
                response_time = elapsed_time
                response_length = str(len(response.text))
                if response.ok:
                    response_message = "OK"
                    success = "true"
                    exception = ""
                else:
                    response_message = "KO"
                    success = "false"
                    exception = str(response.reason)

                binary_codecs = [
                    "base64",
                    "base_64",
                    "bz2",
                    "hex",
                    "quopri",
                    "quotedprintable",
                    "quoted_printable",
                    "uu",
                    "zip",
                    "zlib",
                ]
                data_type = "binary" if response.encoding in binary_codecs else "text"
                bytes_sent = "0"
                group_threads = str(self.user_count)
                all_threads = str(self.runner.user_count)
                latency = "0"
                idle_time = "0"
                connect = "0"

                self.add_result(
                    timestamp,
                    response_time,
                    name,
                    status_code,
                    response_message,
                    thread_name,
                    data_type,
                    success,
                    exception,
                    response_length,
                    bytes_sent,
                    group_threads,
                    all_threads,
                    latency,
                    idle_time,
                    connect,
                )
            except:
                logging.error("failed to log result")
            return response

        return wrapper

    def add_result(
            self,
            timestamp,
            response_time,
            name,
            status_code,
            response_message,
            thread_name,
            data_type,
            success,
            exception,
            response_length,
            bytes_sent,
            group_threads,
            all_threads,
            latency,
            idle_time,
            connect,
    ):
        row = [
            timestamp,
            response_time,
            name,
            status_code,
            response_message,
            thread_name,
            data_type,
            success,
            exception,
            response_length,
            bytes_sent,
            group_threads,
            all_threads,
            latency,
            idle_time,
            connect,
        ]
        if len(self.csv_results) >= self.flush_size:
            self._flush_to_log()
        self.csv_results.append(self.field_delimiter.join(row))

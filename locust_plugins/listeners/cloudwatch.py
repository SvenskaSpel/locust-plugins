import logging
from gevent import queue

log = logging.getLogger(__name__)


class RequestResult:
    STATUS_SUCCESS = "SUCCESS"

    STATUS_FAILURE = "FAILURE"

    def __init__(self, host, request_type, name, response_time, response_length, exception, start_time, url):
        self.timestamp = start_time
        self.request_type = request_type
        self.name = name
        self.response_time = response_time
        self.host = host
        self.url = url

        if exception:
            self.status = RequestResult.STATUS_FAILURE
            self.response_length = 0
            self.exception = exception
        else:
            self.status = RequestResult.STATUS_SUCCESS
            self.response_length = response_length
            self.exception = ""

    def get_all_metrics(self):
        cw_metrics_for_request = [self.get_cw_metrics_response_time_record(), self.get_cw_metrics_count_record()]
        if resp_size_rec := self.get_cw_metrics_response_size_record():
            cw_metrics_for_request.append(resp_size_rec)
        if fail_count_rec := self.get_cw_metrics_failure_count_record():
            cw_metrics_for_request.append(fail_count_rec)
        return cw_metrics_for_request

    def get_cw_metrics_failure_count_record(self):
        dimensions = self.get_metric_dimensions()
        result = {}

        if self.status == RequestResult.STATUS_FAILURE:
            result = {
                "MetricName": "FailureCount",
                "Dimensions": dimensions,
                "Timestamp": self.timestamp,
                "Value": 1,
                "Unit": "Count",
            }

        return result

    def get_cw_metrics_response_size_record(self):
        dimensions = self.get_metric_dimensions()

        result = {}

        if self.status == RequestResult.STATUS_SUCCESS:
            result = {
                "MetricName": "ResponseSize_Bytes",
                "Dimensions": dimensions,
                "Timestamp": self.timestamp,
                "Value": self.response_length,
                "Unit": "Bytes",
            }

        return result

    def get_cw_metrics_response_time_record(self):
        dimensions = self.get_metric_dimensions()
        result = {
            "MetricName": "ResponseTime_ms",
            "Dimensions": dimensions,
            "Timestamp": self.timestamp,
            "Value": self.response_time,
            "Unit": "Milliseconds",
        }
        return result

    def get_cw_metrics_count_record(self):
        dimensions = self.get_metric_dimensions()
        result = {
            "MetricName": "RequestCount",
            "Dimensions": dimensions,
            "Timestamp": self.timestamp,
            "Value": 1,
            "Unit": "Count",
        }
        return result

    def get_metric_dimensions(self):
        result = [
            {"Name": "Request", "Value": self.name},
            {"Name": "Method", "Value": self.request_type},
            {"Name": "Host", "Value": self.host},
        ]
        return result

    def api_id(self):
        return f"{self.request_type}-{self.name}"


class ServiceContext:
    def __init__(self, service, environment="perf"):
        self._service = service
        self._environment = environment

    def environment(self):
        return self._environment

    def service(self):
        return self._service

    def name(self):
        return f"{self._environment}-{self._service}"

    def metrics_namespace(self):
        return f"{self._environment}/{self._service}/loadtests"


class CloudwatchAdapter:
    REQUESTS_BATCH_SIZE = 10
    CLOUDWATCH_METRICS_BATCH_SIZE = 15  # Keeping it conservative not to breach the CW limit

    def __init__(self, cloudwatch, locust_env, service_context):
        self.cloudwatch = cloudwatch
        self.locust_env = locust_env
        self.service_context = service_context
        self.request_results_q = queue.Queue(100)
        events = self.locust_env.events
        events.test_start.add_listener(self.on_test_start)
        events.request.add_listener(self.on_request)
        events.test_stop.add_listener(self.on_test_stop)

    def on_test_start(self, environment, **kwargs):
        log.info("Begin setup")

    def on_test_stop(self, environment, **kwargs):
        remaining_requests_metrics_size = self.request_results_q.qsize()
        log.info(f"Posting remaining metrics for {remaining_requests_metrics_size} requests")
        self._post_to_cloudwatch(self._get_cw_metrics_batch(remaining_requests_metrics_size))
        log.info("Clean up on test stop...Done")

    def on_request(
        self,
        request_type,
        name,
        response_time,
        response_length,
        response,
        context,
        exception,
        start_time,
        url,
        **kwargs,
    ):
        request_result = RequestResult(
            self.locust_env.host, request_type, name, response_time, response_length, exception, start_time, url
        )
        self.request_results_q.put(request_result)

        if self.request_results_q.qsize() >= CloudwatchAdapter.REQUESTS_BATCH_SIZE:
            self._post_to_cloudwatch(self._get_cw_metrics_batch())

    def _get_cw_metrics_batch(self, request_batch_size=REQUESTS_BATCH_SIZE):
        cw_metrics_batch = []
        processed_request_count = 0
        while processed_request_count < request_batch_size:
            request_result = self.request_results_q.get()
            cw_metrics_batch.extend(request_result.get_all_metrics())
            processed_request_count += 1
        return cw_metrics_batch

    def _post_to_cloudwatch(self, cw_metrics_batch):
        while len(cw_metrics_batch) > 0:
            current_batch = cw_metrics_batch[: CloudwatchAdapter.CLOUDWATCH_METRICS_BATCH_SIZE]
            cw_metrics_batch = cw_metrics_batch[CloudwatchAdapter.CLOUDWATCH_METRICS_BATCH_SIZE :]
            if len(current_batch) > 0:
                try:
                    self.cloudwatch.put_metric_data(
                        Namespace=self.service_context.metrics_namespace(), MetricData=current_batch
                    )
                    log.debug(f"Posted {len(current_batch)} metrics to cloudwatch")
                except Exception as e:
                    print(str(e))

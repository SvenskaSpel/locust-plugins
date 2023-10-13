import logging
from gevent import queue
from locust_plugins import missing_extra

log = logging.getLogger(__name__)

try:
    import boto3
except ModuleNotFoundError:
    missing_extra("boto3", "boto3")


class RequestResult:
    """
    Represents the object the holds the outcome of request measurement from locust. Contains all the data
    passed to the on request event hook.
    It also contains all the methods which will produce the Cloudwatch metric records based on locust
    measurements.
    """

    STATUS_SUCCESS = "SUCCESS"

    STATUS_FAILURE = "FAILURE"

    def __init__(self, host, request_type, name, response_time, response_length, exception, start_time, url):
        """
        Collects all the data of a request. If there is an exception then marks the internal
        status accordingly. Also ensures that length and exception are initialised accordingly.
        """
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
        """
        Gets all metrics related to a request. Response time, Request count are mandatory.
        Depending on success or failure we can either have Response size or Failure count metric
        respectively.
        """
        cw_metrics_for_request = [self.get_cw_metrics_response_time_record(), self.get_cw_metrics_count_record()]
        if resp_size_rec := self.get_cw_metrics_response_size_record():
            cw_metrics_for_request.append(resp_size_rec)
        if fail_count_rec := self.get_cw_metrics_failure_count_record():
            cw_metrics_for_request.append(fail_count_rec)
        return cw_metrics_for_request

    def get_cw_metrics_failure_count_record(self):
        """
        Creates a Cloudwatch metric record for FailureCount if the request failed.
        """
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
        """
        Creates a Cloudwatch metric record for Response size if the request succeeded.
        """
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
        """
        Creates a Cloudwatch metric record for response time.
        """
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
        """
        Creates a Cloudwatch metric record for request count.
        """
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
        """
        Provides a collection of generic dimensions which are attached to all cloud watch metrics.
        Helps in identifying the individual type of request and hence different metrics could be plotted
        for them.
        """
        result = [
            {"Name": "Request", "Value": self.name},
            {"Name": "Method", "Value": self.request_type},
            {"Name": "Host", "Value": self.host},
        ]
        return result

    def api_id(self):
        """
        A way to uniquely identify the request based on request_type (GET, POST etc.) and
        the name of the request as given in the locust task.
        """
        return f"{self.request_type}-{self.name}"


class CloudwatchAdapter:
    """
    The primary class which does the actual work for pushing metrics to cloudwatch using the provided
    cloudwatch client (boto3). If it is not provided then the boto3 based client with basic configuration
    is created. It does not push all metrics in one go since talking to cloudwatch incurs
    cost. So it holds them in locally (in a queue) and then sends them in batches to cloudwatch
    """

    REQUESTS_BATCH_SIZE = 10
    CLOUDWATCH_METRICS_BATCH_SIZE = 15  # Keeping it conservative not to breach the CW limit

    def __init__(self, locust_env, service_name, environment="perf", cloudwatch=None):
        if cloudwatch is None:
            self.cloudwatch = boto3.client("cloudwatch")
        else:
            self.cloudwatch = cloudwatch
        self.locust_env = locust_env
        self._service = service_name
        self._environment = environment
        # The queue that hold the metrics locally.
        self.request_results_q = queue.Queue(100)
        events = self.locust_env.events
        events.test_start.add_listener(self.on_test_start)
        events.request.add_listener(self.on_request)
        events.test_stop.add_listener(self.on_test_stop)

    def metrics_namespace(self):
        return f"{self._environment}/{self._service}/loadtests"

    def on_test_start(self, environment, **kwargs):
        log.debug("Begin setup")

    def on_test_stop(self, environment, **kwargs):
        remaining_requests_metrics_size = self.request_results_q.qsize()
        log.debug(f"Posting remaining metrics for {remaining_requests_metrics_size} requests")
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
        # pylint: disable=unused-argument
        request_result = RequestResult(
            self.locust_env.host, request_type, name, response_time, response_length, exception, start_time, url
        )
        self.request_results_q.put(request_result)  # Adding to local queue

        # Once REQUESTS_BATCH_SIZE requests have been collected then it is time to post the data to CW.
        if self.request_results_q.qsize() >= CloudwatchAdapter.REQUESTS_BATCH_SIZE:
            self._post_to_cloudwatch(self._get_cw_metrics_batch())

    def _get_cw_metrics_batch(self, request_batch_size=REQUESTS_BATCH_SIZE):
        """
        Takes each request result and converts into metric records. Given that for a request
        there could be 3 metric records, those will be created and returned.
        """
        cw_metrics_batch = []
        processed_request_count = 0
        while processed_request_count < request_batch_size:
            request_result = self.request_results_q.get()
            cw_metrics_batch.extend(request_result.get_all_metrics())
            processed_request_count += 1
        return cw_metrics_batch

    def _post_to_cloudwatch(self, cw_metrics_batch):
        """
        When posting to cloudwatch we have to ensure that the batch request is within the limit of
        a max cloudwatch request size. We are roughly estimating it to be CLOUDWATCH_METRICS_BATCH_SIZE.
        So when we process REQUESTS_BATCH_SIZE requests we will potentially get 3 * REQUESTS_BATCH_SIZE
        metric records. Posting all of them at one go may exceed the cloudwatch limit. So we are using
        a different limit (CLOUDWATCH_METRICS_BATCH_SIZE) to ensure these are kept separate.
        This code pushs all the metrics collected locally as multiple batches to cloudwatch.
        """
        while len(cw_metrics_batch) > 0:
            current_batch = cw_metrics_batch[: CloudwatchAdapter.CLOUDWATCH_METRICS_BATCH_SIZE]
            cw_metrics_batch = cw_metrics_batch[CloudwatchAdapter.CLOUDWATCH_METRICS_BATCH_SIZE :]
            if len(current_batch) > 0:
                try:
                    self.cloudwatch.put_metric_data(Namespace=self.metrics_namespace(), MetricData=current_batch)
                    log.debug(f"Posted {len(current_batch)} metrics to cloudwatch")
                except Exception as e:
                    print(str(e))

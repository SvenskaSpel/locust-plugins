import logging
import time
from locust import runners, TaskSet
import gevent


class TaskSetRPS(TaskSet):
    """
    A task set that allows locust to limit the number of requests by sleeping to reach a target RPS
    """

    _failed_to_reach_rps_target = False

    def __init__(self, parent):
        super().__init__(parent)
        self._previous_time = 0.0
        self._rps_fail = False

    def rps_sleep(self, rps):
        current_time = float(time.time())
        if runners.locust_runner is None:  # this happens when debugging (running a single locust)
            return
        next_time = self._previous_time + runners.locust_runner.user_count / rps
        if current_time > next_time:
            if runners.locust_runner.state == runners.STATE_RUNNING and not TaskSetRPS._failed_to_reach_rps_target:
                logging.warning("Failed to reach target rps, even after rampup has finished")
                TaskSetRPS._failed_to_reach_rps_target = True  # stop logging
            self._previous_time = current_time
            return

        self._previous_time = next_time
        gevent.sleep(next_time - current_time)

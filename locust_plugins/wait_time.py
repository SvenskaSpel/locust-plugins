import logging
import time
from collections import deque, namedtuple
from locust import events, runners
from locust import constant_pacing
from typing import Any

_last_run = 0.0
_warning_emitted = False
_target_missed = False
_ips_window = deque()  # an implicitly sorted list of when iterations where started
IPS_WINDOW_SIZE = 20


@events.quitting.add_listener
def quitting(**_kwargs: Any):
    if _warning_emitted:
        print(
            "Failed to reach targeted number of iterations per second (at some point during the test). Probably caused by target system overload or too few clients"
        )


# This wait time function to calculate when the next iteration should be run in order to achieve the desired number of Iterations Per Second for the whole locust instance
def constant_total_ips(ips: float):
    def func(user):
        global _warning_emitted, _target_missed, _last_run

        runner = user.environment.runner
        if runner is None:  # happens when debugging a single locust
            runner = namedtuple("FakeRunner", ["target_user_count", "state"])(1, runners.STATE_RUNNING)

        delay = runner.target_user_count / ips
        current_time = time.monotonic()

        # As the delay calculation will not always be able to compensate (particularly when iteration times differ a lot),
        # we compensate up to 10% for the last IPS_WINDOW_SIZE seconds worth of throughput. This will allow us to temporarily
        # over/undershoot the target rate, but get the right rate over time.
        while _ips_window and _ips_window[0] < current_time - IPS_WINDOW_SIZE:
            _ips_window.popleft()
        previous_rate = len(_ips_window) / IPS_WINDOW_SIZE
        _ips_window.append(current_time)
        rate_diff = previous_rate - ips
        delay = delay * (1 + max(min(rate_diff, 0.1), -0.1) / ips)

        next_time = _last_run + delay
        if current_time > next_time:
            if runner.state == runners.STATE_RUNNING and _target_missed and not _warning_emitted:
                logging.warning("Failed to reach target ips, even after rampup has finished")
                _warning_emitted = True  # stop logging
            _target_missed = True
            _last_run = current_time
            return 0
        _target_missed = False
        _last_run = next_time
        return delay

    return func


# inverted versions of common functions
def constant_ips(ips: float):
    return constant_pacing(1.0 / ips)


def constant_total_pacing(seconds: float):
    return constant_total_ips(1.0 / seconds)

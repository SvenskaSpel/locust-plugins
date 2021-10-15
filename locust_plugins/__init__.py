__version__ = "1.7.1"

from .wait_time import constant_ips, constant_total_ips
from .debug import run_single_user
import locust
from locust import TaskSet
from locust.user.task import DefaultTaskSet
from locust import events
from locust.exception import StopUser
from locust.env import Environment
from locust.runners import Runner, WorkerRunner
import logging
from functools import wraps
import configargparse


@events.init_command_line_parser.add_listener
def add_checks_arguments(parser: configargparse.ArgumentParser):
    checks = parser.add_argument_group(
        "locust-plugins - Checks",
        "Sets locust's exit code to 3 if any of these thresholds were not met",
    )
    checks.add_argument(
        "--check-rps",
        type=float,
        help="Requests per second",
        env_var="LOCUST_CHECK_RPS",
        default=0.0,
    )
    checks.add_argument(
        "--check-fail-ratio",
        type=float,
        help="Ratio of failed requests (0.0-1.0)",
        env_var="LOCUST_CHECK_FAIL_RATIO",
        default=1.0,
    )
    checks.add_argument(
        "--check-avg-response-time",
        type=float,
        help="Average response time",
        env_var="LOCUST_CHECK_AVG_RESPONSE_TIME",
        default=-1,
    )
    run_info = parser.add_argument_group(
        "locust-plugins - Run info",
        "Extra run info for listeners",
    )
    run_info.add_argument(
        "--test-env",
        type=str,
        help='Name of target system/environment (e.g. "staging")',
        env_var="LOCUST_TEST_ENV",
        default="",
    )
    run_info.add_argument(
        "--test-version",
        type=str,
        help="Identifier for version of the loadtest/system under test (typically a git hash or GUID)",
        env_var="LOCUST_TEST_VERSION",
        default="",
    )
    run_info.add_argument(
        "--grafana-url",
        type=str,
        help="URL to Grafana dashboard (used by TimescaleListener)",
        env_var="LOCUST_GRAFANA_URL",
        default="",
    )
    other = parser.add_argument_group(
        "locust-plugins - Extras",
    )
    # fix for https://github.com/locustio/locust/issues/1085
    other.add_argument(
        "-i",
        "--iterations",
        type=int,
        help="Dont run more than this number of task iterations and terminate once they have finished",
        env_var="LOCUST_ITERATIONS",
        default=0,
    )
    other.add_argument(
        "--console-stats-interval",
        type=int,
        help="Interval at which to print locust stats to command line",
        env_var="LOCUST_CONSOLE_STATS_INTERVAL",
        default=locust.stats.CONSOLE_STATS_INTERVAL_SEC,
    )


@events.test_start.add_listener
def set_up_iteration_limit(environment: Environment, **_kwargs):
    options = environment.parsed_options
    locust.stats.CONSOLE_STATS_INTERVAL_SEC = environment.parsed_options.console_stats_interval
    if options.iterations:
        runner: Runner = environment.runner
        runner.iterations_started = 0
        runner.iteration_target_reached = False

        def iteration_limit_wrapper(method):
            @wraps(method)
            def wrapped(self, task):
                if runner.iterations_started == options.iterations:
                    if not runner.iteration_target_reached:
                        runner.iteration_target_reached = True
                        logging.info(
                            f"Iteration limit reached ({options.iterations}), stopping Users at the start of their next task run"
                        )
                    if runner.user_count == 1:
                        logging.info("Last user stopped, quitting runner")
                        runner.quit()
                    raise StopUser()
                runner.iterations_started = runner.iterations_started + 1
                method(self, task)

            return wrapped

        # monkey patch TaskSets to add support for iterations limit. Not ugly at all :)
        TaskSet.execute_task = iteration_limit_wrapper(TaskSet.execute_task)
        DefaultTaskSet.execute_task = iteration_limit_wrapper(DefaultTaskSet.execute_task)


@events.quitting.add_listener
def do_checks(environment, **_kw):
    if isinstance(environment.runner, WorkerRunner):
        return

    stats = environment.runner.stats.total
    fail_ratio = stats.fail_ratio
    total_rps = stats.total_rps
    avg_response_time = stats.avg_response_time

    opts = environment.parsed_options
    check_rps = opts.check_rps
    check_fail_ratio = opts.check_fail_ratio
    check_avg_response_time = opts.check_avg_response_time

    if fail_ratio > check_fail_ratio:
        logging.info(f"CHECK FAILED: fail ratio was {(fail_ratio*100):.2f}% (threshold {(check_fail_ratio*100):.2f}%)")
        environment.process_exit_code = 3
    else:
        logging.debug(
            f"CHECK SUCCESSFUL: fail ratio was {(fail_ratio*100):.2f}% (threshold {(check_fail_ratio*100):.2f}%)"
        )

    if total_rps < check_rps:
        logging.info(f"CHECK FAILED: total rps was {total_rps:.1f} (threshold {check_rps:.1f})")
        environment.process_exit_code = 3
    else:
        logging.debug(f"CHECK SUCCESSFUL: total rps was {total_rps:.1f} (threshold {check_rps:.1f})")

    if check_avg_response_time > 0:
        if avg_response_time > check_avg_response_time:
            logging.info(
                f"CHECK FAILED: avg response time was {avg_response_time:.1f} (threshold {check_avg_response_time:.1f})"
            )
            environment.process_exit_code = 3
        else:
            logging.debug(
                f"CHECK SUCCESSFUL: avg response time was {avg_response_time:.1f} (threshold {check_avg_response_time:.1f})"
            )

from .wait_time import constant_ips, constant_total_ips
from .listeners import Timescale
import locust
from locust.user.task import DefaultTaskSet, TaskSet
from locust import events
from locust.exception import StopUser
from locust.env import Environment
from locust.argument_parser import LocustArgumentParser
from locust.runners import Runner, WorkerRunner
import logging
from functools import wraps


@events.init_command_line_parser.add_listener
def add_arguments(parser: LocustArgumentParser):
    checks = parser.add_argument_group(
        "locust-plugins - Checks",
        "Sets locust's exit code to 3 if any of these thresholds were not met",
    )
    checks.add_argument(
        "--check-rps",
        type=float,
        help="Requests per second",
        env_var="LOCUST_CHECK_RPS",
    )
    checks.add_argument(
        "--check-fail-ratio",
        type=float,
        help="Ratio of failed requests (0.0-1.0)",
        env_var="LOCUST_CHECK_FAIL_RATIO",
    )
    checks.add_argument(
        "--check-avg-response-time",
        type=float,
        help="Average response time",
        env_var="LOCUST_CHECK_AVG_RESPONSE_TIME",
    )
    locust_dashboards = parser.add_argument_group(
        "locust-plugins - Locust Dashboards",
        "Timescale + Grafana Dashboards",
    )
    locust_dashboards.add_argument(
        "--timescale",
        action="store_true",
        help="Enable Timescale logging https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/timescale/",
        env_var="LOCUST_TIMESCALE",
        default=False,
    )
    locust_dashboards.add_argument(
        "--grafana-url",
        type=str,
        help="URL to Grafana dashboard (used by Timescale listener)",
        env_var="LOCUST_GRAFANA_URL",
        default="http://localhost:3000/d/qjIIww4Zz?",
    )
    locust_dashboards.add_argument(
        "--pghost",
        type=str,
        help="",
        env_var="PGHOST",
        default="localhost",
    )
    locust_dashboards.add_argument(
        "--pgport",
        type=str,
        help="",
        env_var="PGPORT",
        default="",
    )
    locust_dashboards.add_argument(
        "--pgpassword",
        type=str,
        help="",
        env_var="PGPASSWORD",
        default="",
    )
    locust_dashboards.add_argument(
        "--pguser",
        type=str,
        help="",
        env_var="PGUSER",
        default="",
    )
    locust_dashboards.add_argument(
        "--pgdatabase",
        type=str,
        help="",
        env_var="PGDATABASE",
        default="",
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
        "--profile",
        type=str,
        help="Load profile (a user-configurable string, like any config value it can be accessed using environment.parsed_options.profile)",
        env_var="LOCUST_PROFILE",
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
        "--description",
        type=str,
        env_var="LOCUST_DESCRIPTION",
        default="",
        help="Description of the test being run",
    )
    run_info.add_argument(
        "--override-plan-name",
        type=str,
        help="Override test plan name in Timescale, default is to use locustfile file name",
        env_var="LOCUST_OVERRIDE_PLAN_NAME",
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
        help="Run at most this number of task iterations and terminate once they have finished",
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
    other.add_argument(
        "--ips",
        type=float,
        help="Replace all wait_time:s with global iterations-per-second limiter",
        env_var="LOCUST_IPS",
        default=0,
    )


_timescale_added = False


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if environment.parsed_options.timescale:
        global _timescale_added
        if not _timescale_added:
            Timescale(env=environment)
            _timescale_added = True


@events.test_start.add_listener
def set_up_iteration_limit(environment: Environment, **kwargs):
    options = environment.parsed_options
    locust.stats.CONSOLE_STATS_INTERVAL_SEC = environment.parsed_options.console_stats_interval
    if options.iterations:
        runner: Runner = environment.runner
        runner.iterations_started = 0
        runner.iteration_target_reached = False
        logging.debug(f"Iteration limit set to {options.iterations}")

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

    if options.ips:
        for user_class in environment.runner.user_classes:
            user_class.wait_time = constant_total_ips(options.ips)


@events.quitting.add_listener
def do_checks(environment, **_kw):
    if isinstance(environment.runner, WorkerRunner):
        return

    stats = environment.runner.stats.total
    fail_ratio = stats.fail_ratio
    total_rps = stats.total_rps
    avg_response_time = stats.avg_response_time

    opts = environment.parsed_options
    check_fail_ratio = opts.check_fail_ratio
    check_rps = opts.check_rps
    check_avg_response_time = opts.check_avg_response_time

    if check_fail_ratio is not None:
        if fail_ratio > check_fail_ratio:
            logging.info(
                f"CHECK FAILED: fail ratio was {(fail_ratio*100):.2f}% (threshold {(check_fail_ratio*100):.2f}%)"
            )
            environment.process_exit_code = 3
        else:
            logging.debug(
                f"CHECK SUCCESSFUL: fail ratio was {(fail_ratio*100):.2f}% (threshold {(check_fail_ratio*100):.2f}%)"
            )
        opts.exit_code_on_error = 0

    if check_rps is not None:
        if total_rps < check_rps:
            logging.info(f"CHECK FAILED: total rps was {total_rps:.1f} (threshold {check_rps:.1f})")
            environment.process_exit_code = 3
        else:
            logging.debug(f"CHECK SUCCESSFUL: total rps was {total_rps:.1f} (threshold {check_rps:.1f})")

    if check_avg_response_time is not None:
        if avg_response_time > check_avg_response_time:
            logging.info(
                f"CHECK FAILED: avg response time was {avg_response_time:.1f} (threshold {check_avg_response_time:.1f})"
            )
            environment.process_exit_code = 3
        else:
            logging.debug(
                f"CHECK SUCCESSFUL: avg response time was {avg_response_time:.1f} (threshold {check_avg_response_time:.1f})"
            )

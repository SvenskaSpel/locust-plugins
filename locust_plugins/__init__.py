__version__ = "1.0.17"
from .wait_time import constant_ips, constant_total_ips
from .debug import run_single_user
from locust import User, constant, TaskSet
from locust import events
from locust.exception import StopUser
from locust.env import Environment
from locust.runners import Runner
import logging

# Monkey patch User while waiting for everyone else to see the light:
# https://github.com/locustio/locust/issues/1308
User.wait_time = constant(0)


@events.init_command_line_parser.add_listener
def add_checks_arguments(parser):
    checks = parser.add_argument_group(
        "Checks", "Sets locust's exit code to 2 if any of these thresholds were not met (added by locust-plugins)"
    )
    checks.add_argument("--check-rps", type=float, help="Requests per second", env_var="LOCUST_CHECK_RPS", default=0.0)
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
        default=float("inf"),
    )
    other = parser.add_argument_group("Plugins", "Other extra parameters added by locust-plugins")
    # fix for https://github.com/locustio/locust/issues/1085
    other.add_argument(
        "-i",
        "--iterations",
        type=int,
        help="Dont run more than this number of task iterations and terminate once they have finished",
        env_var="LOCUST_ITERATIONS",
        default=0,
    )


@events.test_start.add_listener
def set_up_iteration_limit(environment: Environment, **_kwargs):
    if environment.parsed_options.iterations:
        runner: Runner = environment.runner
        runner.iterations_started = 0
        runner.iteration_target_reached = False

        # monkey patch Runner to add support for iterations limit
        _execute_next_task = TaskSet.execute_next_task

        def execute_next_task_with_iteration_limit(self: TaskSet):
            if runner.iterations_started == environment.parsed_options.iterations:
                if not runner.iteration_target_reached:
                    runner.iteration_target_reached = True
                    logging.info(
                        f"Iteration limit reached ({environment.parsed_options.iterations}), stopping Users at the start of their next task run"
                    )
                if runner.user_count == 1:
                    logging.debug("Last user stopped, quitting runner")
                    runner.quit()
                raise StopUser()
            runner.iterations_started = runner.iterations_started + 1
            _execute_next_task(self)

        TaskSet.execute_next_task = execute_next_task_with_iteration_limit


@events.quitting.add_listener
def do_checks(environment, **_kw):
    stats = environment.runner.stats.total
    fail_ratio = stats.fail_ratio
    total_rps = stats.total_rps
    avg_response_time = stats.avg_response_time

    opts = environment.parsed_options
    check_rps = opts.check_rps
    check_fail_ratio = opts.check_fail_ratio
    check_avg_response_time = opts.check_avg_response_time

    if fail_ratio > check_fail_ratio:
        logging.info(f"Check failed: fail ratio was {fail_ratio:.1f} (threshold {check_fail_ratio:.1f})")
        environment.process_exit_code = 2
    if total_rps < check_rps:
        logging.info(f"Check failed: total rps was {total_rps:.1f} (threshold {check_rps:.1f})")
        environment.process_exit_code = 2
    if avg_response_time > check_avg_response_time:
        logging.info(
            f"Check failed: avg response time was {avg_response_time:.1f} (threshold {check_avg_response_time:.1f})"
        )
        environment.process_exit_code = 2

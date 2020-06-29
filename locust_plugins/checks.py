from locust import events
import logging

# Usage example:
# locust -f my_locustfile_that_imports_locust_plugins.py -u 1 -t 60 --headless --check-rps 5 --check-fail-ratio 0.05 --check-avg-response-time 50
# This will set locust's exit code to failed (2) if any of the following are not met:
# * At least 5 requests/s
# * At most 5% errors
# * At most 50ms average response times
# (all values are for the whole run)


@events.init_command_line_parser.add_listener
def add_checks_to_arguments(parser):
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

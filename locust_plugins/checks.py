from locust import events
import logging


@events.init_command_line_parser.add_listener
def add_checks_to_arguments(parser):
    checks = parser.add_argument_group("Checks")
    checks.add_argument(
        "--check-rps", type=float, help="Set bad exit code if RPS was lower than this", env_var="LOCUST_CHECK_RPS"
    )
    checks.add_argument(
        "--check-error-pct",
        type=float,
        help="Set bad exit code if error percentage was higher than this",
        env_var="LOCUST_CHECK_ERROR_PCT",
    )


@events.quitting.add_listener
def do_checks(environment, **_kw):
    fail_ratio = environment.runner.stats.total.fail_ratio
    total_rps = environment.runner.stats.total.total_rps

    check_rps = environment.parsed_options.check_rps
    check_error_pct = environment.parsed_options.check_error_pct

    if check_error_pct is not None and fail_ratio > check_error_pct:
        logging.info(f"Fail ratio was {fail_ratio:.1f}, exceeding the threshold of {check_error_pct:.1f}")
        environment.process_exit_code = 2
    if check_rps is not None and total_rps < check_rps:
        logging.info(f"Total rps was {total_rps:.1f}, failed to reach {check_rps:.1f}")
        environment.process_exit_code = 2

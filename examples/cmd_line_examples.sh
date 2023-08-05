locust --help
# use --help for more info on command line parameters

locust -t 60 --headless --check-rps 5 --check-fail-ratio 0.05 --check-avg-response-time 50
# Set locust's exit code to failed (2) if any of the following criteria are not met at the end of the run:
# * At least 5 requests/s
# * At most 5% errors
# * At most 50ms average response times

locust -u 5 -t 60 --headless -i 10
# Stop locust after 10 task iterations (this is an upper bound, so you can be sure no more than 10 of iterations will be done)
# Note that in a distributed run the parameter needs to be set on the workers, it is (currently) not distributed from master to worker.

locust --headless --timescale
# Log results to a Timescale database, see https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/dashboards/

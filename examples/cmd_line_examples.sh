# for command line options to work, you need to run a locust file that imports locust_plugins

locust -u 1 -t 60 --headless --check-rps 5 --check-fail-ratio 0.05 --check-avg-response-time 50
# Set locust's exit code to failed (2) if any of the following are not met:
# * At least 5 requests/s
# * At most 5% errors
# * At most 50ms average response times
# (all values are for the whole run)

locust -u 5 -t 60 --headless -i 10
# Stop locust after 10 task iterations (this is an upper bound, so you can be sure no more than 10 of iterations will be done)
# Note that the limit is applied *per worker* in a distributed run. So if you, for example, have 2 workers you will run 20 requests.
# It is (currently) not distributed from master to worker.

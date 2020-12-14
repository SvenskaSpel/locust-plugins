# TimescaleListener logs Locust samples & events to a Postgres Timescale database.
# This makes it possible to monitor a run in real time using Grafana, as well as
# making it easy to go back to an old run to analyze results.
#
# 1. Set up Timescale for your Postgres https://docs.timescale.com/latest/getting-started/setup
# 2. Set up the tables https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/timescale_schema.sql
# 3. Set the standard postgres env vars (PGHOST, PGPORT etc) to point TimescaleListener to your Postgres https://www.postgresql.org/docs/current/libpq-envars.html
# 4. Set up Grafana, and import the dashboard https://grafana.com/grafana/dashboards/10878
# 5. Set the env var LOCUST_GRAFANA_URL to link to your Grafana
#    (e.g. export LOCUST_GRAFANA_URL=https://my.grafana.host.com/d/qjIIww4Zz/locust?orgId=1)
# 6. Run your tests. If you get an error about "Make sure the TimescaleDB extension has been preloaded", have a look at
#    https://github.com/SvenskaSpel/locust-plugins/issues/11

# Example output:
# ~ locust --headless -f mytestplan.py
# [2020-12-13 19:07:55,426] myhost/INFO/root: Follow test run here: https://my.grafana.host.com/d/qjIIww4Zz/locust?orgId=1&var-testplan=mytestplan&from=1607882875426&to=now
# [2020-12-13 19:07:55,456] myhost/INFO/locust.main: No run time limit set, use CTRL+C to interrupt.
# [2020-12-13 19:07:55,456] myhost/INFO/locust.main: Starting Locust 1.4.1
# ...
# KeyboardInterrupt
# 2020-12-13T18:07:57Z
# [2020-12-13 19:07:57,633] myhost/INFO/locust.main: Running teardowns...
# [2020-12-13 19:07:58,623] myhost/INFO/root: Report: https://my.grafana.host.com/d/qjIIww4Zz/locust?orgId=1&var-testplan=mytestplan&from=1607882875426&to=1607882879506
# [2020-12-13 19:07:58,623] myhost/INFO/locust.main: Shutting down (exit code 0), bye.
# ...

from locust_plugins.listeners import TimescaleListener
from locust import HttpUser, task, events


class MyHttpUser(HttpUser):
    @task
    def index(self):
        self.client.post("/authentication/1.0/getResults", {"username": "something"})

    host = "http://example.com"


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    TimescaleListener(env=environment, testplan="timescale_listener_ex", target_env="myTestEnv")

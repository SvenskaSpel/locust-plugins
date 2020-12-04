# TimescaleListener logs Locust samples & events to a Postgres Timescale database.
# This makes it possible to monitor a run in real time using Grafana, as well as
# making it easy to go back to an old run to analyze results.
#
# 1. Set up Timescale for your Postgres: https://docs.timescale.com/latest/getting-started/setup
# 2. Set up the table: executing timescale_schema.sql
# 3. Set the standard postgres env vars (like PGHOST, PGPORT etc) to point TimescaleListener to your Postgres.
#    TimescaleListener will automatically output a link to your dashboard using the env var LOCUST_GRAFANA_URL
#    (e.g. export LOCUST_GRAFANA_URL=https://my.grafana.host.com/d/qjIIww4Zz/locust?orgId=1)
# 4. Run your tests
# 5. Import this dashboard into grafana to visualize the results: https://grafana.com/grafana/dashboards/10878


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

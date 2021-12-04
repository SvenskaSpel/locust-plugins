The Timescale listener logs Locust samples & events to a Postgres/Timescale database.

This makes it possible to monitor a run in real time using Grafana, analyzing results and errors. As the data is permanently stored in a database it makes it easy to go back to an old run to review & compare results.

In order to feed locust requests into Timescale, all you need to do is add a listener in your locustfile:

```
@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    listeners.Timescale(env=environment, testplan="timescale_listener_ex")
```

# docker-compose-based Timescale + Grafana

Assuming you have docker installed, you can start Postgres/Timescale and Grafana, with the correct tables set up in Timescale and the appropriate dashboards just run `locust-compose up`:

```
~ locust-compose up
+ docker compose -f <your pip install folder>/locust_plugins/timescale/docker-compose.yml up
[+] Running 3/3
 ⠿ Container timescale_postgres_1       Started
 ⠿ Container timescale_grafana_1        Started
 ⠿ Container timescale_setup_grafana_1  Started
Attaching to grafana_1, postgres_1, setup_grafana_1
...
---------------------------------------------------------------------------------------------------------------------------------
setup_grafana_1  | You can now connect to Grafana, the main dashboard is at http://localhost:3000/d/qjIIww4Zz?from=now-15m&to=now
---------------------------------------------------------------------------------------------------------------------------------
```

Follow the link and you will find your fresh (empty) main Locust dashboard, used for analyzing test runs.

If you hadn't already guessed, `locust-compose` is just a thin wrapper around docker-compose. If you want to shut down Postgres and Grafana, run:

```
~ locust-compose down
```


The Timescale data is persisted (survives shutting down the docker containers), but if you edit the grafana dashboards themselves you should save your changes somewhere else.

## Manual setup

1. Set up a Postgres instance (or use the dockerized one provided by the above command, which uses cyberw/locust-timescale:latest)
2. Export the regular Postgres environment variables to point to your instance (PGHOST, PGPORT, PGUSER, PGPASSWORD)
3. If you didnt Set up the tables  (run it something like this: psql < timescale_schema.sql)
https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/timescale_schema.sql

If you already have a Grafana installed, edit the variables in [grafana_setup.sh](grafana_setup.sh) and run it. This will set up a datasource pointing to your Timescale and import the Locust dashboards from grafana.com. If you prefer, you can do it manually from here: https://grafana.com/grafana/dashboards/10878


# 2. Set up the tables  (run it something like this: PGPORT=5432 PGHOST=localhost psql < timescale_schema.sql)
# 6. Run your tests. If you get an error about "Make sure the TimescaleDB extension has been preloaded", have a look at
#    https://github.com/SvenskaSpel/locust-plugins/issues/11

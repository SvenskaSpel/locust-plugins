Locust enables you to log requests & run events to a Postgres/Timescale database.

This data can then be monitored and analyzed in Grafana in real time, or after the test has completed. The dashboards also make it easy to find old test runs and compare results over time.

In order to log Locust's requests and run data into Timescale you add `--timescale` to the command line. But first you need to set up Timescale.

# docker-compose-based Timescale + Grafana

Assuming you have docker installed, you can start Postgres/Timescale and Grafana, with the correct tables set up in Timescale and the appropriate dashboards just run `locust-compose up`:

```
~ locust-compose up
+ docker compose -f /usr/local/lib/python3.9/site-packages/locust_plugins/timescale/docker-compose.yml up
[+] Running 6/6
 ⠿ Network timescale_timenet            Created
 ⠿ Volume "timescale_grafana_data"      Created
 ⠿ Volume "timescale_postgres_data"     Created
 ⠿ Container timescale_grafana_1        Started
 ⠿ Container timescale_postgres_1       Started
 ⠿ Container timescale_setup_grafana_1  Started
Attaching to grafana_1, postgres_1, setup_grafana_1
...
---------------------------------------------------------------------------------------------------------------------------------
setup_grafana_1  | You can now connect to Grafana, the main dashboard is at http://localhost:3000/d/qjIIww4Zz?from=now-15m&to=now
---------------------------------------------------------------------------------------------------------------------------------
```

Follow the link and you will find your fresh (empty) main Locust dashboard, used for analyzing test runs.

You can now run a locust test like this:

locust --timescale --headless

If you hadn't already guessed it from the output, `locust-compose` is just a thin wrapper around `docker-compose`. When you are finished testing, just press CTRL-C or run `locust-compose down`

Both timescale data and any grafana dashboard edits are persisted as docker volumes even if you shut it down. To remove the data run `locust-compose rm`.

For security reasons, the ports for logging to Timescale and accessing Grafana only accessible on localhost. If you want them to be reachable from the outside (e.g. to run a distributed test with workers running on a different machine), edit the docker-compose.yml file.

## Manual setup

1. Set up a Postgres instance (or use the dockerized one provided by the above command, which uses cyberw/locust-timescale:latest)
2. Export the regular Postgres environment variables to point to your instance (PGHOST, PGPORT, PGUSER, PGPASSWORD)
3. If you didnt Set up the tables  (run it something like this: psql < timescale_schema.sql)
https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/timescale/locust-timescale/timescale_schema.sql

If you already have a Grafana installed, edit the variables in [grafana_setup.sh](locust-timescale/grafana_setup.sh) and use it to set up a datasource pointing to your Timescale and import the Locust dashboards from grafana.com. If you prefer, you can do it manually from here: https://grafana.com/grafana/dashboards/10878


# 2. Set up the tables  (run it something like this: PGPORT=5432 PGHOST=localhost psql < timescale_schema.sql)
# 6. Run your tests. If you get an error about "Make sure the TimescaleDB extension has been preloaded", have a look at
#    https://github.com/SvenskaSpel/locust-plugins/issues/11

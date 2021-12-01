# Timescale + Grafana setup

## Docker compose

Start Postgres/Timescale and Grafana in docker, with the correct tables set up in Timescale and the appropriate dashboards set up in Grafana:

```
docker-compose up
```

Grafana is now accessible on http://localhost:3000, and (postgres on localhost:5432)

## Manual setup

If you already have a Grafana installed, edit the variables in [grafana_setup.sh](grafana_setup.sh) and run it. This will set up a datasource pointing to your Timescale and import the Locust dashboards from grafana.com. If you prefer, you can do it manually from here: https://grafana.com/grafana/dashboards/10878

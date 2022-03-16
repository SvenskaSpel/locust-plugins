#!/bin/bash -e

# edit this as necessary, if you want to set up the DS/dashboards on a different environment
export GRAFANA_HOST="${GRAFANA_HOST:=http://localhost:3000}"
export GRAFANA_CRED="${GRAFANA_CRED:=admin:admin}"
export GRAFANA_OVERWRITE="${GRAFANA_OVERWRITE:=false}" # change to true to overwrite pre-existing dashboards (update to latest version from grafana.com)
export PGHOST="${PGHOST:=postgres}"
export PGPORT="${PGPORT:=5432}"
export DS_NAME="${DS_NAME:=locust_timescale}"

${BASH_SOURCE%/*}/create_datasource.sh
${BASH_SOURCE%/*}/import_dashboards.sh
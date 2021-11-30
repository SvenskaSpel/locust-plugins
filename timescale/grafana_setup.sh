#!/bin/bash -e

# edit this as necessary, if you want to set up the DS/dashboards on a different environment
export GRAFANA_HOST="http://grafana:3000"
export GRAFANA_CRED="admin:admin"
export GRAFANA_DATASOURCE="timescale"
export TIMESCALE_HOST="localhost"
export TIMESCALE_PORT="5432"

${BASH_SOURCE%/*}/create_datasource.sh
${BASH_SOURCE%/*}/import_dashboards.sh

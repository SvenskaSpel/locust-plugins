FROM timescale/timescaledb:latest-pg13
# Dependencies needed for doing setup against Grafana
RUN apk add bash curl jq
# Import table and index definitions on startup
COPY *.sql /docker-entrypoint-initdb.d/

FROM timescale/timescaledb:latest-pg13
ENV POSTGRES_PASSWORD password
ENV TIMESCALEDB_TELEMETRY off
RUN apk add bash curl jq # these are not actually used by timescale itself, but for doing setup against Grafana
COPY timescale_schema.sql /docker-entrypoint-initdb.d/
COPY *.sh /commands/

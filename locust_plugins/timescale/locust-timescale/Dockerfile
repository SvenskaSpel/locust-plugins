FROM timescale/timescaledb:latest-pg13
ENV POSTGRES_PASSWORD password
ENV TIMESCALEDB_TELEMETRY off
# Dependencies needed for doing setup against Grafana
RUN apk add bash curl jq  
# Grafana setup commands
COPY *.sh /commands/    
# Import table and index definitions on startup
COPY timescale_schema.sql /docker-entrypoint-initdb.d/

-- this needs to be in a different file/session, so that timescale extension is properly initialized

SELECT create_hypertable('request', 'time');
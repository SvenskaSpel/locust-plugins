-- see https://github.com/timescale/timescaledb for more info on setting up timescale

CREATE TABLE public.request
(
    "time" timestamp with time zone NOT NULL,
    run_id timestamp with time zone NOT NULL,
    exception text COLLATE pg_catalog."default",
    greenlet_id integer NOT NULL,
    loadgen text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    request_type text COLLATE pg_catalog."default" NOT NULL,
    response_length integer,
    response_time double precision,
    success smallint NOT NULL,
    testplan text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
CREATE INDEX request_time_idx
    ON public.request USING btree
    ("time" DESC)
    TABLESPACE pg_default;
CREATE TRIGGER ts_insert_blocker
    BEFORE INSERT
    ON public.request
    FOR EACH ROW
    EXECUTE PROCEDURE _timescaledb_internal.insert_blocker();

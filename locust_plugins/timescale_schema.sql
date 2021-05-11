-- Warning, there have been some issues applying this. If you do have issues, do not hesitate to contact me (cyberw)

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.3
-- Dumped by pg_dump version 11.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: timescaledb; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS timescaledb WITH SCHEMA public;


--
-- Name: EXTENSION timescaledb; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION timescaledb IS 'Enables scalable inserts and complex queries for time-series data';


--
-- Name: tablefunc; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS tablefunc WITH SCHEMA public;


--
-- Name: EXTENSION tablefunc; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION tablefunc IS 'functions that manipulate whole tables, including crosstab';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: request; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.request (
    "time" timestamp with time zone NOT NULL,
    run_id timestamp with time zone NOT NULL,
    exception text,
    greenlet_id integer NOT NULL,
    pid integer NOT NULL,
    loadgen text NOT NULL,
    name text NOT NULL,
    request_type text NOT NULL,
    response_length integer,
    response_time double precision,
    success smallint NOT NULL,
    testplan character varying(30) NOT NULL,
    context jsonb
);


ALTER TABLE public.request OWNER TO postgres;

--
-- Name: _hyper_2_11_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_11_chunk (
    CONSTRAINT constraint_11 CHECK ((("time" >= '2019-07-18 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-07-25 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_11_chunk OWNER TO postgres;

--
-- Name: _hyper_2_13_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_13_chunk (
    CONSTRAINT constraint_13 CHECK ((("time" >= '2019-08-01 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-08-08 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_13_chunk OWNER TO postgres;

--
-- Name: _hyper_2_15_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_15_chunk (
    CONSTRAINT constraint_15 CHECK ((("time" >= '2019-08-08 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-08-15 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_15_chunk OWNER TO postgres;

--
-- Name: _hyper_2_18_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_18_chunk (
    CONSTRAINT constraint_18 CHECK ((("time" >= '2019-08-22 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-08-29 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_18_chunk OWNER TO postgres;

--
-- Name: _hyper_2_20_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_20_chunk (
    CONSTRAINT constraint_20 CHECK ((("time" >= '2019-08-29 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-09-05 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_20_chunk OWNER TO postgres;

--
-- Name: _hyper_2_22_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_22_chunk (
    CONSTRAINT constraint_22 CHECK ((("time" >= '2019-09-05 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-09-12 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_22_chunk OWNER TO postgres;

--
-- Name: _hyper_2_24_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_24_chunk (
    CONSTRAINT constraint_24 CHECK ((("time" >= '2019-09-12 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-09-19 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_24_chunk OWNER TO postgres;

--
-- Name: _hyper_2_26_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_26_chunk (
    CONSTRAINT constraint_26 CHECK ((("time" >= '2019-09-19 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-09-26 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_26_chunk OWNER TO postgres;

--
-- Name: _hyper_2_28_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_28_chunk (
    CONSTRAINT constraint_28 CHECK ((("time" >= '2019-09-26 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-10-03 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_28_chunk OWNER TO postgres;

--
-- Name: _hyper_2_30_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_30_chunk (
    CONSTRAINT constraint_30 CHECK ((("time" >= '2019-10-03 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-10-10 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_30_chunk OWNER TO postgres;

--
-- Name: _hyper_2_32_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_32_chunk (
    CONSTRAINT constraint_32 CHECK ((("time" >= '2019-10-17 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-10-24 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_32_chunk OWNER TO postgres;

--
-- Name: _hyper_2_34_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_34_chunk (
    CONSTRAINT constraint_34 CHECK ((("time" >= '2019-10-24 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-10-31 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_34_chunk OWNER TO postgres;

--
-- Name: _hyper_2_36_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_36_chunk (
    CONSTRAINT constraint_36 CHECK ((("time" >= '2019-10-31 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-11-07 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_36_chunk OWNER TO postgres;

--
-- Name: _hyper_2_38_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_38_chunk (
    CONSTRAINT constraint_38 CHECK ((("time" >= '2019-11-07 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-11-14 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_38_chunk OWNER TO postgres;

--
-- Name: _hyper_2_40_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_40_chunk (
    CONSTRAINT constraint_40 CHECK ((("time" >= '2019-11-14 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-11-21 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_40_chunk OWNER TO postgres;

--
-- Name: _hyper_2_42_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_42_chunk (
    CONSTRAINT constraint_42 CHECK ((("time" >= '2019-11-21 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-11-28 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_42_chunk OWNER TO postgres;

--
-- Name: _hyper_2_44_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_44_chunk (
    CONSTRAINT constraint_44 CHECK ((("time" >= '2019-11-28 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-12-05 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_44_chunk OWNER TO postgres;

--
-- Name: _hyper_2_46_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_46_chunk (
    CONSTRAINT constraint_46 CHECK ((("time" >= '2019-12-05 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-12-12 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_46_chunk OWNER TO postgres;

--
-- Name: _hyper_2_48_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_48_chunk (
    CONSTRAINT constraint_48 CHECK ((("time" >= '2019-12-12 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-12-19 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_48_chunk OWNER TO postgres;

--
-- Name: _hyper_2_4_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_4_chunk (
    CONSTRAINT constraint_4 CHECK ((("time" >= '2019-06-27 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-07-04 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_4_chunk OWNER TO postgres;

--
-- Name: _hyper_2_50_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_50_chunk (
    CONSTRAINT constraint_50 CHECK ((("time" >= '2019-12-19 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-12-26 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_50_chunk OWNER TO postgres;

--
-- Name: _hyper_2_53_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_53_chunk (
    CONSTRAINT constraint_53 CHECK ((("time" >= '2019-12-26 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-01-02 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_53_chunk OWNER TO postgres;

--
-- Name: _hyper_2_55_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_55_chunk (
    CONSTRAINT constraint_55 CHECK ((("time" >= '2020-01-02 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-01-09 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_55_chunk OWNER TO postgres;

--
-- Name: _hyper_2_58_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_58_chunk (
    CONSTRAINT constraint_58 CHECK ((("time" >= '2020-01-09 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-01-16 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_58_chunk OWNER TO postgres;

--
-- Name: _hyper_2_63_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_63_chunk (
    CONSTRAINT constraint_63 CHECK ((("time" >= '2020-01-16 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-01-23 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_63_chunk OWNER TO postgres;

--
-- Name: _hyper_2_66_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_66_chunk (
    CONSTRAINT constraint_66 CHECK ((("time" >= '2020-01-23 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-01-30 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_66_chunk OWNER TO postgres;

--
-- Name: _hyper_2_69_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_69_chunk (
    CONSTRAINT constraint_69 CHECK ((("time" >= '2020-01-30 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-02-06 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_69_chunk OWNER TO postgres;

--
-- Name: _hyper_2_6_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_6_chunk (
    CONSTRAINT constraint_6 CHECK ((("time" >= '2019-07-04 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-07-11 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_6_chunk OWNER TO postgres;

--
-- Name: _hyper_2_72_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_72_chunk (
    CONSTRAINT constraint_72 CHECK ((("time" >= '2020-02-06 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-02-13 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_72_chunk OWNER TO postgres;

--
-- Name: _hyper_2_9_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_9_chunk (
    CONSTRAINT constraint_9 CHECK ((("time" >= '2019-07-11 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-07-18 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.request);


ALTER TABLE _timescaledb_internal._hyper_2_9_chunk OWNER TO postgres;

--
-- Name: testrun; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.testrun (
    id timestamp with time zone NOT NULL,
    testplan text NOT NULL,
    profile_name text,
    num_clients integer NOT NULL,
    rps double precision,
    description text,
    end_time timestamp with time zone,
    env character varying(10) NOT NULL,
    username character varying(12),
    gitrepo character varying(40),
    rps_avg numeric,
    resp_time_avg numeric,
    changeset_guid character varying(36),
    fail_ratio double precision,
    requests integer
);


ALTER TABLE public.testrun OWNER TO postgres;

--
-- Name: _hyper_3_10_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_10_chunk (
    CONSTRAINT constraint_10 CHECK (((id >= '2019-07-18 00:00:00+00'::timestamp with time zone) AND (id < '2019-07-25 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_10_chunk OWNER TO postgres;

--
-- Name: _hyper_3_12_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_12_chunk (
    CONSTRAINT constraint_12 CHECK (((id >= '2019-08-01 00:00:00+00'::timestamp with time zone) AND (id < '2019-08-08 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_12_chunk OWNER TO postgres;

--
-- Name: _hyper_3_14_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_14_chunk (
    CONSTRAINT constraint_14 CHECK (((id >= '2019-08-08 00:00:00+00'::timestamp with time zone) AND (id < '2019-08-15 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_14_chunk OWNER TO postgres;

--
-- Name: _hyper_3_16_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_16_chunk (
    CONSTRAINT constraint_16 CHECK (((id >= '2019-08-15 00:00:00+00'::timestamp with time zone) AND (id < '2019-08-22 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_16_chunk OWNER TO postgres;

--
-- Name: _hyper_3_17_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_17_chunk (
    CONSTRAINT constraint_17 CHECK (((id >= '2019-08-22 00:00:00+00'::timestamp with time zone) AND (id < '2019-08-29 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_17_chunk OWNER TO postgres;

--
-- Name: _hyper_3_19_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_19_chunk (
    CONSTRAINT constraint_19 CHECK (((id >= '2019-08-29 00:00:00+00'::timestamp with time zone) AND (id < '2019-09-05 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_19_chunk OWNER TO postgres;

--
-- Name: _hyper_3_21_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_21_chunk (
    CONSTRAINT constraint_21 CHECK (((id >= '2019-09-05 00:00:00+00'::timestamp with time zone) AND (id < '2019-09-12 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_21_chunk OWNER TO postgres;

--
-- Name: _hyper_3_23_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_23_chunk (
    CONSTRAINT constraint_23 CHECK (((id >= '2019-09-12 00:00:00+00'::timestamp with time zone) AND (id < '2019-09-19 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_23_chunk OWNER TO postgres;

--
-- Name: _hyper_3_25_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_25_chunk (
    CONSTRAINT constraint_25 CHECK (((id >= '2019-09-19 00:00:00+00'::timestamp with time zone) AND (id < '2019-09-26 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_25_chunk OWNER TO postgres;

--
-- Name: _hyper_3_27_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_27_chunk (
    CONSTRAINT constraint_27 CHECK (((id >= '2019-09-26 00:00:00+00'::timestamp with time zone) AND (id < '2019-10-03 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_27_chunk OWNER TO postgres;

--
-- Name: _hyper_3_29_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_29_chunk (
    CONSTRAINT constraint_29 CHECK (((id >= '2019-10-03 00:00:00+00'::timestamp with time zone) AND (id < '2019-10-10 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_29_chunk OWNER TO postgres;

--
-- Name: _hyper_3_31_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_31_chunk (
    CONSTRAINT constraint_31 CHECK (((id >= '2019-10-17 00:00:00+00'::timestamp with time zone) AND (id < '2019-10-24 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_31_chunk OWNER TO postgres;

--
-- Name: _hyper_3_33_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_33_chunk (
    CONSTRAINT constraint_33 CHECK (((id >= '2019-10-24 00:00:00+00'::timestamp with time zone) AND (id < '2019-10-31 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_33_chunk OWNER TO postgres;

--
-- Name: _hyper_3_35_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_35_chunk (
    CONSTRAINT constraint_35 CHECK (((id >= '2019-10-31 00:00:00+00'::timestamp with time zone) AND (id < '2019-11-07 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_35_chunk OWNER TO postgres;

--
-- Name: _hyper_3_37_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_37_chunk (
    CONSTRAINT constraint_37 CHECK (((id >= '2019-11-07 00:00:00+00'::timestamp with time zone) AND (id < '2019-11-14 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_37_chunk OWNER TO postgres;

--
-- Name: _hyper_3_39_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_39_chunk (
    CONSTRAINT constraint_39 CHECK (((id >= '2019-11-14 00:00:00+00'::timestamp with time zone) AND (id < '2019-11-21 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_39_chunk OWNER TO postgres;

--
-- Name: _hyper_3_41_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_41_chunk (
    CONSTRAINT constraint_41 CHECK (((id >= '2019-11-21 00:00:00+00'::timestamp with time zone) AND (id < '2019-11-28 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_41_chunk OWNER TO postgres;

--
-- Name: _hyper_3_43_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_43_chunk (
    CONSTRAINT constraint_43 CHECK (((id >= '2019-11-28 00:00:00+00'::timestamp with time zone) AND (id < '2019-12-05 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_43_chunk OWNER TO postgres;

--
-- Name: _hyper_3_45_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_45_chunk (
    CONSTRAINT constraint_45 CHECK (((id >= '2019-12-05 00:00:00+00'::timestamp with time zone) AND (id < '2019-12-12 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_45_chunk OWNER TO postgres;

--
-- Name: _hyper_3_47_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_47_chunk (
    CONSTRAINT constraint_47 CHECK (((id >= '2019-12-12 00:00:00+00'::timestamp with time zone) AND (id < '2019-12-19 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_47_chunk OWNER TO postgres;

--
-- Name: _hyper_3_49_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_49_chunk (
    CONSTRAINT constraint_49 CHECK (((id >= '2019-12-19 00:00:00+00'::timestamp with time zone) AND (id < '2019-12-26 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_49_chunk OWNER TO postgres;

--
-- Name: _hyper_3_52_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_52_chunk (
    CONSTRAINT constraint_52 CHECK (((id >= '2019-12-26 00:00:00+00'::timestamp with time zone) AND (id < '2020-01-02 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_52_chunk OWNER TO postgres;

--
-- Name: _hyper_3_54_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_54_chunk (
    CONSTRAINT constraint_54 CHECK (((id >= '2020-01-02 00:00:00+00'::timestamp with time zone) AND (id < '2020-01-09 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_54_chunk OWNER TO postgres;

--
-- Name: _hyper_3_57_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_57_chunk (
    CONSTRAINT constraint_57 CHECK (((id >= '2020-01-09 00:00:00+00'::timestamp with time zone) AND (id < '2020-01-16 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_57_chunk OWNER TO postgres;

--
-- Name: _hyper_3_5_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_5_chunk (
    CONSTRAINT constraint_5 CHECK (((id >= '2019-06-27 00:00:00+00'::timestamp with time zone) AND (id < '2019-07-04 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_5_chunk OWNER TO postgres;

--
-- Name: _hyper_3_60_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_60_chunk (
    CONSTRAINT constraint_60 CHECK (((id >= '2019-01-10 00:00:00+00'::timestamp with time zone) AND (id < '2019-01-17 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_60_chunk OWNER TO postgres;

--
-- Name: _hyper_3_61_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_61_chunk (
    CONSTRAINT constraint_61 CHECK (((id >= '2020-01-16 00:00:00+00'::timestamp with time zone) AND (id < '2020-01-23 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_61_chunk OWNER TO postgres;

--
-- Name: _hyper_3_64_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_64_chunk (
    CONSTRAINT constraint_64 CHECK (((id >= '2020-01-23 00:00:00+00'::timestamp with time zone) AND (id < '2020-01-30 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_64_chunk OWNER TO postgres;

--
-- Name: _hyper_3_67_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_67_chunk (
    CONSTRAINT constraint_67 CHECK (((id >= '2020-01-30 00:00:00+00'::timestamp with time zone) AND (id < '2020-02-06 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_67_chunk OWNER TO postgres;

--
-- Name: _hyper_3_70_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_70_chunk (
    CONSTRAINT constraint_70 CHECK (((id >= '2020-02-06 00:00:00+00'::timestamp with time zone) AND (id < '2020-02-13 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_70_chunk OWNER TO postgres;

--
-- Name: _hyper_3_7_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_7_chunk (
    CONSTRAINT constraint_7 CHECK (((id >= '2019-07-04 00:00:00+00'::timestamp with time zone) AND (id < '2019-07-11 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_7_chunk OWNER TO postgres;

--
-- Name: _hyper_3_8_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_3_8_chunk (
    CONSTRAINT constraint_8 CHECK (((id >= '2019-07-11 00:00:00+00'::timestamp with time zone) AND (id < '2019-07-18 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.testrun);


ALTER TABLE _timescaledb_internal._hyper_3_8_chunk OWNER TO postgres;

--
-- Name: user_count; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_count (
    testplan character varying(30) NOT NULL,
    user_count integer NOT NULL,
    "time" timestamp with time zone NOT NULL,
    run_id timestamp with time zone
);


ALTER TABLE public.user_count OWNER TO postgres;

--
-- Name: _hyper_4_51_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_4_51_chunk (
    CONSTRAINT constraint_51 CHECK ((("time" >= '2019-12-19 00:00:00+00'::timestamp with time zone) AND ("time" < '2019-12-26 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.user_count);


ALTER TABLE _timescaledb_internal._hyper_4_51_chunk OWNER TO postgres;

--
-- Name: _hyper_4_56_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_4_56_chunk (
    CONSTRAINT constraint_56 CHECK ((("time" >= '2020-01-02 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-01-09 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.user_count);


ALTER TABLE _timescaledb_internal._hyper_4_56_chunk OWNER TO postgres;

--
-- Name: _hyper_4_59_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_4_59_chunk (
    CONSTRAINT constraint_59 CHECK ((("time" >= '2020-01-09 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-01-16 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.user_count);


ALTER TABLE _timescaledb_internal._hyper_4_59_chunk OWNER TO postgres;

--
-- Name: _hyper_4_62_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_4_62_chunk (
    CONSTRAINT constraint_62 CHECK ((("time" >= '2020-01-16 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-01-23 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.user_count);


ALTER TABLE _timescaledb_internal._hyper_4_62_chunk OWNER TO postgres;

--
-- Name: _hyper_4_65_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_4_65_chunk (
    CONSTRAINT constraint_65 CHECK ((("time" >= '2020-01-23 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-01-30 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.user_count);


ALTER TABLE _timescaledb_internal._hyper_4_65_chunk OWNER TO postgres;

--
-- Name: _hyper_4_68_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_4_68_chunk (
    CONSTRAINT constraint_68 CHECK ((("time" >= '2020-01-30 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-02-06 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.user_count);


ALTER TABLE _timescaledb_internal._hyper_4_68_chunk OWNER TO postgres;

--
-- Name: _hyper_4_71_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_4_71_chunk (
    CONSTRAINT constraint_71 CHECK ((("time" >= '2020-02-06 00:00:00+00'::timestamp with time zone) AND ("time" < '2020-02-13 00:00:00+00'::timestamp with time zone)))
)
INHERITS (public.user_count);


ALTER TABLE _timescaledb_internal._hyper_4_71_chunk OWNER TO postgres;

--
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events (
    "time" timestamp with time zone NOT NULL,
    text text NOT NULL
);


ALTER TABLE public.events OWNER TO postgres;

--
-- Name: _hyper_3_10_chunk 10_6_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_10_chunk
    ADD CONSTRAINT "10_6_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_12_chunk 12_7_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_12_chunk
    ADD CONSTRAINT "12_7_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_14_chunk 14_8_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_14_chunk
    ADD CONSTRAINT "14_8_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_16_chunk 16_9_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_16_chunk
    ADD CONSTRAINT "16_9_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_17_chunk 17_10_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_17_chunk
    ADD CONSTRAINT "17_10_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_19_chunk 19_11_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_19_chunk
    ADD CONSTRAINT "19_11_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_21_chunk 21_12_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_21_chunk
    ADD CONSTRAINT "21_12_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_23_chunk 23_13_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_23_chunk
    ADD CONSTRAINT "23_13_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_25_chunk 25_14_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_25_chunk
    ADD CONSTRAINT "25_14_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_27_chunk 27_15_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_27_chunk
    ADD CONSTRAINT "27_15_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_29_chunk 29_16_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_29_chunk
    ADD CONSTRAINT "29_16_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_31_chunk 31_17_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_31_chunk
    ADD CONSTRAINT "31_17_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_33_chunk 33_18_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_33_chunk
    ADD CONSTRAINT "33_18_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_35_chunk 35_19_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_35_chunk
    ADD CONSTRAINT "35_19_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_37_chunk 37_20_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_37_chunk
    ADD CONSTRAINT "37_20_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_39_chunk 39_21_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_39_chunk
    ADD CONSTRAINT "39_21_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_41_chunk 41_22_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_41_chunk
    ADD CONSTRAINT "41_22_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_43_chunk 43_23_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_43_chunk
    ADD CONSTRAINT "43_23_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_45_chunk 45_24_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_45_chunk
    ADD CONSTRAINT "45_24_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_47_chunk 47_25_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_47_chunk
    ADD CONSTRAINT "47_25_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_49_chunk 49_26_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_49_chunk
    ADD CONSTRAINT "49_26_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_52_chunk 52_27_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_52_chunk
    ADD CONSTRAINT "52_27_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_54_chunk 54_28_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_54_chunk
    ADD CONSTRAINT "54_28_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_57_chunk 57_29_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_57_chunk
    ADD CONSTRAINT "57_29_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_5_chunk 5_3_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_5_chunk
    ADD CONSTRAINT "5_3_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_60_chunk 60_30_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_60_chunk
    ADD CONSTRAINT "60_30_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_61_chunk 61_31_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_61_chunk
    ADD CONSTRAINT "61_31_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_64_chunk 64_32_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_64_chunk
    ADD CONSTRAINT "64_32_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_67_chunk 67_33_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_67_chunk
    ADD CONSTRAINT "67_33_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_70_chunk 70_34_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_70_chunk
    ADD CONSTRAINT "70_34_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_7_chunk 7_4_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_7_chunk
    ADD CONSTRAINT "7_4_testrun_pkey" PRIMARY KEY (id);


--
-- Name: _hyper_3_8_chunk 8_5_testrun_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_3_8_chunk
    ADD CONSTRAINT "8_5_testrun_pkey" PRIMARY KEY (id);


--
-- Name: testrun testrun_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.testrun
    ADD CONSTRAINT testrun_pkey PRIMARY KEY (id);


--
-- Name: _hyper_2_11_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_11_chunk_request_time_idx ON _timescaledb_internal._hyper_2_11_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_11_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_11_chunk_run_id_idx ON _timescaledb_internal._hyper_2_11_chunk USING btree (run_id);


--
-- Name: _hyper_2_13_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_13_chunk_request_time_idx ON _timescaledb_internal._hyper_2_13_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_13_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_13_chunk_run_id_idx ON _timescaledb_internal._hyper_2_13_chunk USING btree (run_id);


--
-- Name: _hyper_2_15_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_15_chunk_request_time_idx ON _timescaledb_internal._hyper_2_15_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_15_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_15_chunk_run_id_idx ON _timescaledb_internal._hyper_2_15_chunk USING btree (run_id);


--
-- Name: _hyper_2_18_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_18_chunk_request_time_idx ON _timescaledb_internal._hyper_2_18_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_18_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_18_chunk_run_id_idx ON _timescaledb_internal._hyper_2_18_chunk USING btree (run_id);


--
-- Name: _hyper_2_20_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_20_chunk_request_time_idx ON _timescaledb_internal._hyper_2_20_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_20_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_20_chunk_run_id_idx ON _timescaledb_internal._hyper_2_20_chunk USING btree (run_id);


--
-- Name: _hyper_2_22_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_22_chunk_request_time_idx ON _timescaledb_internal._hyper_2_22_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_22_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_22_chunk_run_id_idx ON _timescaledb_internal._hyper_2_22_chunk USING btree (run_id);


--
-- Name: _hyper_2_24_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_24_chunk_request_time_idx ON _timescaledb_internal._hyper_2_24_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_24_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_24_chunk_run_id_idx ON _timescaledb_internal._hyper_2_24_chunk USING btree (run_id);


--
-- Name: _hyper_2_26_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_26_chunk_request_time_idx ON _timescaledb_internal._hyper_2_26_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_26_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_26_chunk_run_id_idx ON _timescaledb_internal._hyper_2_26_chunk USING btree (run_id);


--
-- Name: _hyper_2_28_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_28_chunk_request_time_idx ON _timescaledb_internal._hyper_2_28_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_28_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_28_chunk_run_id_idx ON _timescaledb_internal._hyper_2_28_chunk USING btree (run_id);


--
-- Name: _hyper_2_30_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_30_chunk_request_time_idx ON _timescaledb_internal._hyper_2_30_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_30_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_30_chunk_run_id_idx ON _timescaledb_internal._hyper_2_30_chunk USING btree (run_id);


--
-- Name: _hyper_2_32_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_32_chunk_request_time_idx ON _timescaledb_internal._hyper_2_32_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_32_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_32_chunk_run_id_idx ON _timescaledb_internal._hyper_2_32_chunk USING btree (run_id);


--
-- Name: _hyper_2_34_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_34_chunk_request_time_idx ON _timescaledb_internal._hyper_2_34_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_34_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_34_chunk_run_id_idx ON _timescaledb_internal._hyper_2_34_chunk USING btree (run_id);


--
-- Name: _hyper_2_36_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_36_chunk_request_time_idx ON _timescaledb_internal._hyper_2_36_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_36_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_36_chunk_run_id_idx ON _timescaledb_internal._hyper_2_36_chunk USING btree (run_id);


--
-- Name: _hyper_2_38_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_38_chunk_request_time_idx ON _timescaledb_internal._hyper_2_38_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_38_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_38_chunk_run_id_idx ON _timescaledb_internal._hyper_2_38_chunk USING btree (run_id);


--
-- Name: _hyper_2_40_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_40_chunk_request_time_idx ON _timescaledb_internal._hyper_2_40_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_40_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_40_chunk_run_id_idx ON _timescaledb_internal._hyper_2_40_chunk USING btree (run_id);


--
-- Name: _hyper_2_42_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_42_chunk_request_time_idx ON _timescaledb_internal._hyper_2_42_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_42_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_42_chunk_run_id_idx ON _timescaledb_internal._hyper_2_42_chunk USING btree (run_id);


--
-- Name: _hyper_2_44_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_44_chunk_request_time_idx ON _timescaledb_internal._hyper_2_44_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_44_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_44_chunk_run_id_idx ON _timescaledb_internal._hyper_2_44_chunk USING btree (run_id);


--
-- Name: _hyper_2_46_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_46_chunk_request_time_idx ON _timescaledb_internal._hyper_2_46_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_46_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_46_chunk_run_id_idx ON _timescaledb_internal._hyper_2_46_chunk USING btree (run_id);


--
-- Name: _hyper_2_48_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_48_chunk_request_time_idx ON _timescaledb_internal._hyper_2_48_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_48_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_48_chunk_run_id_idx ON _timescaledb_internal._hyper_2_48_chunk USING btree (run_id);


--
-- Name: _hyper_2_4_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_4_chunk_request_time_idx ON _timescaledb_internal._hyper_2_4_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_4_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_4_chunk_run_id_idx ON _timescaledb_internal._hyper_2_4_chunk USING btree (run_id);


--
-- Name: _hyper_2_50_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_50_chunk_request_time_idx ON _timescaledb_internal._hyper_2_50_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_50_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_50_chunk_run_id_idx ON _timescaledb_internal._hyper_2_50_chunk USING btree (run_id);


--
-- Name: _hyper_2_53_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_53_chunk_request_time_idx ON _timescaledb_internal._hyper_2_53_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_53_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_53_chunk_run_id_idx ON _timescaledb_internal._hyper_2_53_chunk USING btree (run_id);


--
-- Name: _hyper_2_55_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_55_chunk_request_time_idx ON _timescaledb_internal._hyper_2_55_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_55_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_55_chunk_run_id_idx ON _timescaledb_internal._hyper_2_55_chunk USING btree (run_id);


--
-- Name: _hyper_2_58_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_58_chunk_request_time_idx ON _timescaledb_internal._hyper_2_58_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_58_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_58_chunk_run_id_idx ON _timescaledb_internal._hyper_2_58_chunk USING btree (run_id);


--
-- Name: _hyper_2_63_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_63_chunk_request_time_idx ON _timescaledb_internal._hyper_2_63_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_63_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_63_chunk_run_id_idx ON _timescaledb_internal._hyper_2_63_chunk USING btree (run_id);


--
-- Name: _hyper_2_66_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_66_chunk_request_time_idx ON _timescaledb_internal._hyper_2_66_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_66_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_66_chunk_run_id_idx ON _timescaledb_internal._hyper_2_66_chunk USING btree (run_id);


--
-- Name: _hyper_2_69_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_69_chunk_request_time_idx ON _timescaledb_internal._hyper_2_69_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_69_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_69_chunk_run_id_idx ON _timescaledb_internal._hyper_2_69_chunk USING btree (run_id);


--
-- Name: _hyper_2_6_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_6_chunk_request_time_idx ON _timescaledb_internal._hyper_2_6_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_6_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_6_chunk_run_id_idx ON _timescaledb_internal._hyper_2_6_chunk USING btree (run_id);


--
-- Name: _hyper_2_72_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_72_chunk_request_time_idx ON _timescaledb_internal._hyper_2_72_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_72_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_72_chunk_run_id_idx ON _timescaledb_internal._hyper_2_72_chunk USING btree (run_id);


--
-- Name: _hyper_2_9_chunk_request_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_9_chunk_request_time_idx ON _timescaledb_internal._hyper_2_9_chunk USING btree ("time" DESC);


--
-- Name: _hyper_2_9_chunk_run_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_9_chunk_run_id_idx ON _timescaledb_internal._hyper_2_9_chunk USING btree (run_id);


--
-- Name: _hyper_3_10_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_10_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_10_chunk USING btree (id DESC);


--
-- Name: _hyper_3_12_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_12_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_12_chunk USING btree (id DESC);


--
-- Name: _hyper_3_14_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_14_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_14_chunk USING btree (id DESC);


--
-- Name: _hyper_3_16_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_16_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_16_chunk USING btree (id DESC);


--
-- Name: _hyper_3_17_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_17_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_17_chunk USING btree (id DESC);


--
-- Name: _hyper_3_19_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_19_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_19_chunk USING btree (id DESC);


--
-- Name: _hyper_3_21_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_21_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_21_chunk USING btree (id DESC);


--
-- Name: _hyper_3_23_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_23_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_23_chunk USING btree (id DESC);


--
-- Name: _hyper_3_25_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_25_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_25_chunk USING btree (id DESC);


--
-- Name: _hyper_3_27_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_27_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_27_chunk USING btree (id DESC);


--
-- Name: _hyper_3_29_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_29_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_29_chunk USING btree (id DESC);


--
-- Name: _hyper_3_31_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_31_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_31_chunk USING btree (id DESC);


--
-- Name: _hyper_3_33_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_33_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_33_chunk USING btree (id DESC);


--
-- Name: _hyper_3_35_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_35_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_35_chunk USING btree (id DESC);


--
-- Name: _hyper_3_37_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_37_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_37_chunk USING btree (id DESC);


--
-- Name: _hyper_3_39_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_39_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_39_chunk USING btree (id DESC);


--
-- Name: _hyper_3_41_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_41_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_41_chunk USING btree (id DESC);


--
-- Name: _hyper_3_43_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_43_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_43_chunk USING btree (id DESC);


--
-- Name: _hyper_3_45_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_45_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_45_chunk USING btree (id DESC);


--
-- Name: _hyper_3_47_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_47_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_47_chunk USING btree (id DESC);


--
-- Name: _hyper_3_49_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_49_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_49_chunk USING btree (id DESC);


--
-- Name: _hyper_3_52_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_52_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_52_chunk USING btree (id DESC);


--
-- Name: _hyper_3_54_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_54_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_54_chunk USING btree (id DESC);


--
-- Name: _hyper_3_57_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_57_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_57_chunk USING btree (id DESC);


--
-- Name: _hyper_3_5_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_5_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_5_chunk USING btree (id DESC);


--
-- Name: _hyper_3_60_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_60_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_60_chunk USING btree (id DESC);


--
-- Name: _hyper_3_61_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_61_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_61_chunk USING btree (id DESC);


--
-- Name: _hyper_3_64_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_64_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_64_chunk USING btree (id DESC);


--
-- Name: _hyper_3_67_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_67_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_67_chunk USING btree (id DESC);


--
-- Name: _hyper_3_70_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_70_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_70_chunk USING btree (id DESC);


--
-- Name: _hyper_3_7_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_7_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_7_chunk USING btree (id DESC);


--
-- Name: _hyper_3_8_chunk_testrun_id_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_3_8_chunk_testrun_id_idx ON _timescaledb_internal._hyper_3_8_chunk USING btree (id DESC);


--
-- Name: _hyper_4_51_chunk_user_count_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_4_51_chunk_user_count_time_idx ON _timescaledb_internal._hyper_4_51_chunk USING btree ("time" DESC);


--
-- Name: _hyper_4_56_chunk_user_count_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_4_56_chunk_user_count_time_idx ON _timescaledb_internal._hyper_4_56_chunk USING btree ("time" DESC);


--
-- Name: _hyper_4_59_chunk_user_count_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_4_59_chunk_user_count_time_idx ON _timescaledb_internal._hyper_4_59_chunk USING btree ("time" DESC);


--
-- Name: _hyper_4_62_chunk_user_count_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_4_62_chunk_user_count_time_idx ON _timescaledb_internal._hyper_4_62_chunk USING btree ("time" DESC);


--
-- Name: _hyper_4_65_chunk_user_count_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_4_65_chunk_user_count_time_idx ON _timescaledb_internal._hyper_4_65_chunk USING btree ("time" DESC);


--
-- Name: _hyper_4_68_chunk_user_count_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_4_68_chunk_user_count_time_idx ON _timescaledb_internal._hyper_4_68_chunk USING btree ("time" DESC);


--
-- Name: _hyper_4_71_chunk_user_count_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_4_71_chunk_user_count_time_idx ON _timescaledb_internal._hyper_4_71_chunk USING btree ("time" DESC);


--
-- Name: request_time_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX request_time_idx ON public.request USING btree ("time" DESC);


--
-- Name: run_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX run_id_idx ON public.request USING btree (run_id);


--
-- Name: testrun_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX testrun_id_idx ON public.testrun USING btree (id DESC);


--
-- Name: user_count_time_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_count_time_idx ON public.user_count USING btree ("time" DESC);


--
-- Name: request ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.request FOR EACH ROW EXECUTE PROCEDURE _timescaledb_internal.insert_blocker();


--
-- Name: testrun ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.testrun FOR EACH ROW EXECUTE PROCEDURE _timescaledb_internal.insert_blocker();


--
-- Name: user_count ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.user_count FOR EACH ROW EXECUTE PROCEDURE _timescaledb_internal.insert_blocker();


--
-- PostgreSQL database dump complete
--


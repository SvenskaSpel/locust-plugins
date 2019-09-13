import gevent
import gevent.monkey

gevent.monkey.patch_all()
import psycogreen.gevent

psycogreen.gevent.patch_psycopg()
import psycopg2
import os
from contextlib import contextmanager
from psycopg2 import pool, extras  # pylint: disable=unused-import


class CustomerReader:
    """
    A simple library to help locust get and lock test data from a postgres database.
    the approach is fairly naive, dont expect it to scale to huge databases or heavy concurrency.

    This assumes you have a postgres database with a table similar to this: (using smallint instead of booleans for the logged_in flag is a historical accident)
    CREATE TABLE public.customers
    (
        account_id character(10) COLLATE pg_catalog."default",
        ssn character(12) COLLATE pg_catalog."default" NOT NULL,
        logged_in smallint NOT NULL DEFAULT '0'::smallint,
        env character(5) COLLATE pg_catalog."default" NOT NULL,
        last_login timestamp without time zone NOT NULL,
        CONSTRAINT customers_ssn_env UNIQUE (ssn, env)
    )
    CREATE INDEX customers_ssn_env_logged_in_last_login
        ON public.customers USING btree
        (ssn COLLATE pg_catalog."default", env COLLATE pg_catalog."default", logged_in, last_login)
        TABLESPACE pg_default;
    """

    def __init__(self, env):
        self._pool = psycopg2.pool.SimpleConnectionPool(1, 10, host=os.environ["PGHOST"], port="5432")
        self._env = env

    def get(self):
        """Get and lock a customer by setting logged_in in an atomic db operation. Returns a dict."""
        with self._getcursor() as cursor:
            cursor.execute(
                f"UPDATE customers SET logged_in=1, last_login=now() WHERE ssn=(SELECT ssn FROM customers WHERE logged_in=0 AND env='{self._env}' ORDER BY last_login LIMIT 1 FOR UPDATE SKIP LOCKED) AND env='{self._env}' RETURNING account_id,ssn"
            )
            resp = cursor.fetchone()
            return resp

    def release(self, customer):
        """Unlock customer in database (set logged_in to zero)"""
        with self._getcursor() as cursor:
            cursor.execute(
                f"UPDATE customers SET logged_in=0 WHERE ssn='{customer['ssn']}' AND env='{self._env}' RETURNING ssn"
            )
            ssn = cursor.fetchone()[0]
        if ssn != customer["ssn"]:
            raise Exception(f"failed to unlock customer with ssn {ssn}")

    @contextmanager
    def _getcursor(self):
        conn = self._pool.getconn()
        conn.autocommit = True
        try:
            yield conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        finally:
            self._pool.putconn(conn)

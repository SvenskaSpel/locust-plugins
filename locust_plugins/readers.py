import gevent
import gevent.monkey

gevent.monkey.patch_all()
import psycogreen.gevent

psycogreen.gevent.patch_psycopg()
import psycopg2
import os
from contextlib import contextmanager
from psycopg2 import pool, extras, errors  # pylint: disable=unused-import
import csv
import time
import logging


class PostgresReader:
    """
    A simple library to help locust get and lock test data from a postgres database.
    the approach is fairly naive, dont expect it to scale to huge databases or heavy concurrency.

    This assumes you have a postgres database with a table similar to this: (using smallint instead of booleans for the logged_in flag is a historical accident). This may not be an optimal table layout, but maybe you can use it as a starting point.
    CREATE TABLE public.customers
    (
        account_id character(10) COLLATE pg_catalog."default",
        ssn character(12) COLLATE pg_catalog."default" NOT NULL,
        logged_in smallint NOT NULL DEFAULT '0'::smallint,
        last_login timestamp without time zone NOT NULL,
        last_used_by character(12) COLLATE pg_catalog."default",
        CONSTRAINT customers_ssn UNIQUE (ssn)
    )
    CREATE INDEX customers_ssn_env_logged_in_last_login
        ON public.customers USING btree
        (ssn COLLATE pg_catalog."default" COLLATE pg_catalog."default", logged_in, last_login)
        TABLESPACE pg_default;
    """

    def __init__(self, selection):
        """selection that will get appended to the where-clause, e.g. "some_column = 'some_value'" """
        self._pool = psycopg2.pool.SimpleConnectionPool(
            1, 100, host=os.environ["PGHOST"], port="5432", cursor_factory=psycopg2.extras.DictCursor
        )
        self._selection = f" AND {selection}" if selection else ""
        self._delay_warning = 1

    def get(self):
        """Get and lock a customer by setting logged_in in an atomic db operation. Returns a dict."""
        with self.db() as conn:
            start_at = time.time()
            while True:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        f"UPDATE customers SET logged_in=1, last_login=now(), last_used_by='{os.environ['USER']}' WHERE ssn=(SELECT ssn FROM customers WHERE logged_in=0{self._selection} ORDER BY last_login LIMIT 1 FOR UPDATE SKIP LOCKED){self._selection} RETURNING account_id, ssn, last_login"
                    )
                    resp = cursor.fetchone()
                    cursor.close()
                    conn.commit()
                    if start_at + self._delay_warning < time.time():
                        logging.warning(
                            f"Getting a customer took more than {self._delay_warning} seconds (doubling warning threshold for next time)"
                        )
                        self._delay_warning *= 2
                    break
                except psycopg2.OperationalError:
                    # it sucks that we have to do this, but Postgres doesnt guarantee isolation with FOR UPDATE unless we use
                    # ISOLATION_LEVEL_SERIALIZABLE, and then we need to retry "manually" when there is an error.
                    cursor.close()
                    conn.rollback()
            if resp is None:
                raise Exception(
                    f"Didnt get any customer from db. Maybe they were all locked or your filter statement ({self._selection}) was bad?"
                )
            return resp

    def release(self, customer):
        """Unlock customer in database (set logged_in to zero)"""
        with self.db() as conn:
            while True:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        f"UPDATE customers SET logged_in=0, last_used_by='{os.environ['USER']}' WHERE ssn='{customer['ssn']}'{self._selection}"
                    )
                    cursor.close()
                    conn.commit()
                    break
                except psycopg2.OperationalError:
                    cursor.close()
                    conn.rollback()

    @contextmanager
    def db(self):
        conn = self._pool.getconn()
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
        try:
            yield conn
        finally:
            self._pool.putconn(conn)


class CSVReader:
    "Read test data from csv file using an iterator"

    def __init__(self, file):
        try:
            file = open(file)
        except TypeError:
            pass  # "file" was already a pre-opened file-like object
        self.file = file
        self.reader = csv.reader(file)

    def __next__(self):
        try:
            return next(self.reader)
        except StopIteration:
            # reuse file on EOF
            self.file.seek(0, 0)
            return next(self.reader)

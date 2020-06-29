import gevent
import gevent.monkey

gevent.monkey.patch_all()
import psycogreen.gevent

psycogreen.gevent.patch_psycopg()
import psycopg2
import psycopg2.extras
import atexit
import logging
import os
import socket
import sys
from datetime import datetime, timezone

import greenlet
from dateutil import parser
from locust.exception import RescheduleTask, StopUser, CatchResponseError
import subprocess
import locust.env
from typing import List


def create_dbconn():
    try:
        conn = psycopg2.connect(host=os.environ["PGHOST"])
    except Exception:
        logging.error(
            "Use standard postgres env vars to specify where to report locust samples (https://www.postgresql.org/docs/11/libpq-envars.html)"
        )
        raise
    conn.autocommit = True
    return conn


class TimescaleListener:  # pylint: disable=R0902
    """
    Timescale logs locust samples/events to a Postgres Timescale database.
    It relies on the standard postgres env vars (like PGHOST, PGPORT etc).
    You need to set up a timescale table first, as described in listeners_timescale_table.sql
    Follow to intructions here, if you create a new timescaleDB - https://docs.timescale.com/latest/getting-started/setup
    And check tables triggers after restoring DB from listeners_timescale_table.sql to prevent erros for INSERT queries - https://github.com/timescale/timescaledb/issues/1381
    To visualize the data, use grafana and this dashboard: https://grafana.com/grafana/dashboards/10878
    Timescale will automatically output a link to your dashboard using the env var LOCUST_GRAFANA_URL
    (e.g. export LOCUST_GRAFANA_URL=https://my.grafana.host.com/d/qjIIww4Zz/locust?orgId=1)
    """

    def __init__(
        self,
        env: locust.env.Environment,
        testplan: str,
        target_env: str = os.getenv("LOCUST_TEST_ENV", ""),
        profile_name: str = "",
        description: str = "",
    ):
        self.grafana_url = os.environ["LOCUST_GRAFANA_URL"]
        self._conn = create_dbconn()
        self._user_conn = create_dbconn()
        self._testrun_conn = create_dbconn()
        self._events_conn = create_dbconn()
        assert testplan != ""
        self._testplan = testplan
        assert env != ""
        self._env = target_env
        self.env = env
        self._hostname = socket.gethostname()
        self._username = os.getenv("USER", "unknown")
        self._changeset_guid = os.getenv("CHANGESET_GUID")
        self._samples: List[dict] = []
        self._finished = False
        self._profile_name = profile_name
        self._rps = os.getenv("LOCUST_RPS", "0")
        self._description = description
        self._pid = os.getpid()
        self._gitrepo = (
            subprocess.check_output(
                "git remote show origin -n 2>/dev/null | grep h.URL | sed 's/.*://;s/.git$//'",
                shell=True,
                stderr=None,
                universal_newlines=True,
            )
            or None  # default to None instead of empty string
        )
        if is_worker() or is_master():
            # swarm generates the run id for its master and workers
            if "LOCUST_RUN_ID" in os.environ:
                self._run_id = parser.parse(os.environ["LOCUST_RUN_ID"])
            else:
                logging.info(
                    "You are running distributed, but without swarm. run_id:s in Timescale will not match exactly between load gens"
                )
                self._run_id = datetime.now(timezone.utc)
        else:
            # non-swarm runs need to generate the run id here
            self._run_id = datetime.now(timezone.utc)
        if not is_worker():
            logging.info(
                f"Follow test run here: {self.grafana_url}&var-testplan={self._testplan}&from={int(self._run_id.timestamp()*1000)}&to=now"
            )
            self.log_start_testrun()
            self._user_count_logger = gevent.spawn(self._log_user_count)

        self._background = gevent.spawn(self._run)
        events = self.env.events
        events.request_success.add_listener(self.request_success)
        events.request_failure.add_listener(self.request_failure)
        events.quitting.add_listener(self.quitting)
        events.hatch_complete.add_listener(self.hatch_complete)
        atexit.register(self.exit)

    def _log_user_count(self):
        while True:
            self.write_user_count()
            gevent.sleep(2.0)

    def _run(self):
        while True:
            if self._samples:
                # Buffer samples, so that a locust greenlet will write to the new list
                # instead of the one that has been sent into postgres client
                samples_buffer = self._samples
                self._samples = []
                self.write_samples_to_db(samples_buffer)
            else:
                if self._finished:
                    break
            gevent.sleep(0.5)

    def write_user_count(self):
        if self.env.runner is None:
            return  # there is no runner, so nothing to log...
        try:
            with self._user_conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO user_count(time, run_id, testplan, user_count) VALUES (%s, %s, %s, %s)""",
                    (datetime.now(timezone.utc), self._run_id, self._testplan, self.env.runner.user_count),
                )
        except psycopg2.Error as error:
            logging.error("Failed to write user count to Postgresql: " + repr(error))

    def write_samples_to_db(self, samples):
        try:
            with self._conn.cursor() as cur:
                psycopg2.extras.execute_values(
                    cur,
                    """INSERT INTO request(time,run_id,greenlet_id,loadgen,name,request_type,response_time,success,testplan,response_length,exception,pid) VALUES %s""",
                    samples,
                    template="(%(time)s, %(run_id)s, %(greenlet_id)s, %(loadgen)s, %(name)s, %(request_type)s, %(response_time)s, %(success)s, %(testplan)s, %(response_length)s, %(exception)s, %(pid)s)",
                )
        except psycopg2.Error as error:
            logging.error("Failed to write samples to Postgresql timescale database: " + repr(error))

    def quitting(self, **_kwargs):
        self._finished = True
        atexit._clear()  # make sure we dont capture additional ctrl-c:s # pylint: disable=protected-access
        self._background.join(timeout=10)
        if not is_worker():
            self._user_count_logger.kill()
        self.exit()

    def _log_request(self, request_type, name, response_time, response_length, success, exception):
        current_greenlet = greenlet.getcurrent()  # pylint: disable=I1101
        if hasattr(current_greenlet, "minimal_ident"):
            greenlet_id = current_greenlet.minimal_ident
        else:
            greenlet_id = -1  # if no greenlet has been spawned (typically when debugging)

        sample = {
            "time": datetime.now(timezone.utc).isoformat(),
            "run_id": self._run_id,
            "greenlet_id": greenlet_id,
            "loadgen": self._hostname,
            "name": name,
            "request_type": request_type,
            "response_time": response_time,
            "success": success,
            "testplan": self._testplan,
            "pid": self._pid,
        }

        if response_length >= 0:
            sample["response_length"] = response_length
        else:
            sample["response_length"] = None

        if exception:
            if isinstance(exception, CatchResponseError):
                sample["exception"] = str(exception)
            else:
                sample["exception"] = repr(exception)
        else:
            sample["exception"] = None

        self._samples.append(sample)

    def request_success(self, request_type, name, response_time, response_length, **_kwargs):
        self._log_request(request_type, name, response_time, response_length, 1, None)

    def request_failure(self, request_type, name, response_time, response_length, exception, **_kwargs):
        self._log_request(request_type, name, response_time, response_length, 0, exception)

    def log_start_testrun(self):
        num_users = 1
        for index, arg in enumerate(sys.argv):
            if arg == "-u":
                num_users = int(sys.argv[index + 1])
        with self._testrun_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO testrun (id, testplan, profile_name, num_clients, rps, description, env, username, gitrepo, changeset_guid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    self._run_id,
                    self._testplan,
                    self._profile_name,
                    num_users,
                    self._rps,
                    self._description,
                    self._env,
                    self._username,
                    self._gitrepo,
                    self._changeset_guid,
                ),
            )
            cur.execute(
                "INSERT INTO events (time, text) VALUES (%s, %s)",
                (datetime.now(timezone.utc).isoformat(), self._testplan + " started by " + self._username),
            )

    def hatch_complete(self, user_count):
        if not is_worker():  # only log for master/standalone
            end_time = datetime.now(timezone.utc)
            try:
                self._events_conn.cursor().execute(
                    "INSERT INTO events (time, text) VALUES (%s, %s)",
                    (end_time, f"{self._testplan} rampup complete, {user_count} users spawned"),
                )
            except psycopg2.Error as error:
                logging.error(
                    "Failed to insert rampup complete event time to Postgresql timescale database: " + repr(error)
                )

    def log_stop_test_run(self):
        end_time = datetime.now(timezone.utc)
        try:
            with self._testrun_conn.cursor() as cur:
                cur.execute("UPDATE testrun SET end_time = %s where id = %s", (end_time, self._run_id))
                cur.execute("INSERT INTO events (time, text) VALUES (%s, %s)", (end_time, self._testplan + " finished"))
                cur.execute(
                    "UPDATE testrun SET rps_avg = (SELECT ROUND(reqs::numeric / secs::numeric, 1) FROM \
                    (SELECT count(*) AS reqs FROM request WHERE run_id = %s) AS requests, \
                    (SELECT EXTRACT(epoch FROM (SELECT MAX(time)-MIN(time) FROM request WHERE run_id = %s)) AS secs) AS seconds) \
                    WHERE id = %s",
                    (self._run_id, self._run_id, self._run_id),
                )
                cur.execute(
                    "UPDATE testrun SET resp_time_avg = (SELECT ROUND(AVG(response_time)::numeric, 1) FROM request WHERE run_id = %s) WHERE id =  %s",
                    (self._run_id, self._run_id),
                )

        except psycopg2.Error as error:
            logging.error(
                "Failed to update testrun record (or events) with end time to Postgresql timescale database: "
                + repr(error)
            )
        logging.info(
            f"Report: {self.grafana_url}&var-testplan={self._testplan}&from={int(self._run_id.timestamp()*1000)}&to={int((end_time.timestamp()+1)*1000)}\n"
        )

    def exit(self):
        if not is_worker():  # on master or standalone locust run
            self.log_stop_test_run()
        if self._conn:
            self._conn.close()
            self._events_conn.close()
            self._testrun_conn.close()
            self._user_conn.close()


class PrintListener:  # pylint: disable=R0902
    """
    Print every response (useful when debugging a single locust)
    """

    def __init__(self, env: locust.env.Environment, include_length=False, include_time=False):
        env.events.request_success.add_listener(self.request_success)
        env.events.request_failure.add_listener(self.request_failure)
        self.include_length = "length\t" if include_length else ""
        self.include_time = "time                    \t" if include_time else ""
        print(f"\n{self.include_time}type\t{'name'.ljust(50)}\tresponse time\t{self.include_length}exception")

    # @self._events.request_success.add_listener
    def request_success(self, request_type, name, response_time, response_length, **_kwargs):
        self._log_request(request_type, name, response_time, response_length, True, None)

    # @self._events.request_failure.add_listener
    def request_failure(self, request_type, name, response_time, response_length, exception, **_kwargs):
        self._log_request(request_type, name, response_time, response_length, False, exception)

    def _log_request(self, request_type, name, response_time, response_length, success, exception):
        e = "" if exception is None else str(exception)
        if success:
            errortext = e  # should be empty but who knows, maybe there is such a case...
        else:
            errortext = "Failed: " + e
        n = name.ljust(30)
        if self.include_time:
            print(datetime.now(), end="\t")
        if self.include_length:
            print(f"{request_type}\t{n.ljust(50)}\t{round(response_time)}\t{response_length}\t{errortext}")
        else:
            print(f"{request_type}\t{n.ljust(50)}\t{round(response_time)}\t{errortext}")


class RescheduleTaskOnFailListener:
    def __init__(self, env: locust.env.Environment):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        env.events.request_failure.add_listener(self.request_failure)

    def request_failure(self, request_type, name, response_time, response_length, exception, **_kwargs):
        raise RescheduleTask()


class StopUserOnFailListener:
    def __init__(self, env: locust.env.Environment):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        env.events.request_failure.add_listener(self.request_failure)

    def request_failure(self, request_type, name, response_time, response_length, exception, **_kwargs):
        raise StopUser()


class ExitOnFailListener:
    def __init__(self, env: locust.env.Environment):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        env.events.request_failure.add_listener(self.request_failure)

    def request_failure(self, **_kwargs):
        gevent.sleep(0.2)  # wait for other listeners output to flush / write to db
        os._exit(1)


def is_worker():
    return "--worker" in sys.argv


def is_master():
    return "--master" in sys.argv

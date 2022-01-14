from locust.exception import (
    RescheduleTask,
    StopUser,
    CatchResponseError,
    InterruptTaskSet,
)  # need to do this first to make sure monkey patching is done
import gevent
import psycogreen.gevent
import json

psycogreen.gevent.patch_psycopg()
import psycopg2
import psycopg2.extras
import atexit
import logging
import os
import socket
import sys
from datetime import datetime, timezone, timedelta

import greenlet
from dateutil import parser
import subprocess
import locust.env
from typing import List

# pylint: disable=trailing-whitespace # pylint is confused by multiline strings used for SQL


def safe_serialize(obj):
    default = lambda o: f"<<non-serializable: {type(o).__qualname__}>>"
    return json.dumps(obj, default=default)


def print_t(s):
    print(str(s), end="\t")


class Timescale:  # pylint: disable=R0902
    """
    See timescale_listener_ex.py for documentation
    """

    first_instance = True

    def __init__(
        self,
        env: locust.env.Environment,
        testplan: str = None,
    ):
        if not Timescale.first_instance:
            # we should refactor this into a module as it is much more pythonic
            raise Exception(
                "You tried to initialize the Timescale listener twice, maybe both in your locustfile and using command line --timescale? Ignoring second initialization."
            )
        Timescale.first_instance = False
        if testplan:
            self._testplan = testplan  # legacy
        elif env.parsed_options.override_plan_name:
            self._testplan = env.parsed_options.override_plan_name
        else:
            self._testplan = env.parsed_options.locustfile
        self.env = env
        self._samples: List[dict] = []
        self._background = gevent.spawn(self._run)
        self._hostname = socket.gethostname()  # pylint: disable=no-member
        self._username = os.getenv("USER", "unknown")
        self._finished = False
        self._pid = os.getpid()
        events = self.env.events
        events.test_start.add_listener(self.on_start)
        events.request.add_listener(self.on_request)
        events.quitting.add_listener(self.quitting)
        events.spawning_complete.add_listener(self.spawning_complete)
        atexit.register(self.log_stop_test_run)

    def on_start(self, environment: locust.env.Environment):
        try:
            self._conn = self._dbconn()
        except psycopg2.OperationalError as e:
            logging.error(e)
            os._exit(1)
        self._user_conn = self._dbconn()
        self._testrun_conn = self._dbconn()
        self._events_conn = self._dbconn()
        self._rps = os.getenv("LOCUST_RPS", "0")
        try:
            self._gitrepo = subprocess.check_output(
                "git remote show origin -n 2>/dev/null | grep h.URL | sed 's/.*://;s/.git$//' || true",
                shell=True,
                stderr=None,
                universal_newlines=True,
            )
        except:
            # happens on windows
            self._gitrepo = None

        if is_worker() or is_master():
            # swarm generates the run id for its master and workers
            if getattr(environment.parsed_options, "run_id", False):
                self._run_id = parser.parse(environment.parsed_options.run_id)
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
                f"Follow test run here: {self.env.parsed_options.grafana_url}&var-testplan={self._testplan}&from={int(self._run_id.timestamp()*1000)}&to=now"
            )
            self.log_start_testrun()
            self._user_count_logger = gevent.spawn(self._log_user_count)

    def _dbconn(self) -> psycopg2.extensions.connection:
        try:
            conn = psycopg2.connect(
                host=os.environ.get("PGHOST", "localhost"),
                keepalives_idle=120,
                keepalives_interval=20,
                keepalives_count=6,
            )
        except Exception:
            logging.error(
                "Could not connect to postgres. Use standard postgres env vars to specify where to report locust samples (https://www.postgresql.org/docs/11/libpq-envars.html)"
            )
            raise
        conn.autocommit = True
        return conn

    def _log_user_count(self):
        while True:
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
                try:
                    # try to recreate connection
                    self.user_conn = self._dbconn()
                except:
                    pass
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

    def write_samples_to_db(self, samples):
        try:
            with self._conn.cursor() as cur:
                psycopg2.extras.execute_values(
                    cur,
                    """INSERT INTO request(time,run_id,greenlet_id,loadgen,name,request_type,response_time,success,testplan,response_length,exception,pid,url,context) VALUES %s""",
                    samples,
                    template="(%(time)s, %(run_id)s, %(greenlet_id)s, %(loadgen)s, %(name)s, %(request_type)s, %(response_time)s, %(success)s, %(testplan)s, %(response_length)s, %(exception)s, %(pid)s, %(url)s, %(context)s)",
                )
        except psycopg2.Error as error:
            logging.error("Failed to write samples to Postgresql timescale database: " + repr(error))

    def quitting(self, **_kwargs):
        self._finished = True
        atexit._clear()  # make sure we dont capture additional ctrl-c:s # pylint: disable=protected-access
        self._background.join(timeout=10)
        if getattr(self, "_user_count_logger", False):
            self._user_count_logger.kill()
        self.log_stop_test_run()

    def on_request(
        self,
        request_type,
        name,
        response_time,
        response_length,
        exception,
        context,
        start_time=None,
        url=None,
        **_kwargs,
    ):
        success = 0 if exception else 1
        if start_time:
            time = datetime.fromtimestamp(start_time, tz=timezone.utc)
        else:
            # some users may not send start_time, so we just make an educated guess
            # (which will be horribly wrong if users spend a lot of time in a with/catch_response-block)
            time = datetime.now(timezone.utc) - timedelta(milliseconds=response_time or 0)
        greenlet_id = getattr(greenlet.getcurrent(), "minimal_ident", 0)  # if we're debugging there is no greenlet
        sample = {
            "time": time,
            "run_id": self._run_id,
            "greenlet_id": greenlet_id,
            "loadgen": self._hostname,
            "name": name,
            "request_type": request_type,
            "response_time": response_time,
            "success": success,
            "url": url[0:255] if url else None,
            "testplan": self._testplan,
            "pid": self._pid,
            "context": psycopg2.extras.Json(context, safe_serialize),
        }

        if response_length >= 0:
            sample["response_length"] = response_length
        else:
            sample["response_length"] = None

        if exception:
            if isinstance(exception, CatchResponseError):
                sample["exception"] = str(exception)
            else:
                try:
                    sample["exception"] = repr(exception)
                except AttributeError:
                    sample["exception"] = f"{exception.__class__} (and it has no string representation)"
        else:
            sample["exception"] = None

        self._samples.append(sample)

    def log_start_testrun(self):
        with self._testrun_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO testrun (id, testplan, num_clients, rps, description, env, username, gitrepo, changeset_guid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    self._run_id,
                    self._testplan,
                    self.env.parsed_options.num_users or 1,
                    self._rps,
                    self.env.parsed_options.description,
                    self.env.parsed_options.test_env,
                    self._username,
                    self._gitrepo,
                    self.env.parsed_options.test_version,
                ),
            )
            cur.execute(
                "INSERT INTO events (time, text) VALUES (%s, %s)",
                (datetime.now(timezone.utc).isoformat(), self._testplan + " started by " + self._username),
            )

    def spawning_complete(self, user_count):
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
        if is_worker():
            return  # only run on master or standalone
        if not getattr(self, "_testrun_conn", False):
            return  # run never started, so no need to log the end
        end_time = datetime.now(timezone.utc)
        try:
            with self._testrun_conn.cursor() as cur:
                cur.execute("UPDATE testrun SET end_time = %s where id = %s", (end_time, self._run_id))
                cur.execute("INSERT INTO events (time, text) VALUES (%s, %s)", (end_time, self._testplan + " finished"))
                # The AND time > run_id clause in the following statements are there to help Timescale performance
                # We dont use start_time / end_time to calculate RPS, instead we use the time between the actual first and last request
                # (as this is a more accurate measurement of the actual test)
                try:
                    cur.execute(
                        """
UPDATE testrun 
SET (requests, resp_time_avg, rps_avg, fail_ratio) = 
(SELECT reqs, resp_time, reqs / GREATEST(duration, 1), fails / reqs) FROM 
(SELECT 
 COUNT(*)::numeric AS reqs, 
 AVG(response_time)::numeric as resp_time 
 FROM request WHERE run_id = %s AND time > %s) AS _,
(SELECT
 EXTRACT(epoch FROM (SELECT MAX(time)-MIN(time) FROM request WHERE run_id = %s AND time > %s))::numeric AS duration) AS __,
(SELECT 
 COUNT(*)::numeric AS fails 
 FROM request WHERE run_id = %s AND time > %s AND success = 0) AS ___
WHERE id = %s""",
                        [self._run_id] * 7,
                    )
                except psycopg2.errors.DivisionByZero:  # pylint: disable=no-member
                    logging.debug(
                        "Got DivisionByZero error when trying to update testrun into events, most likely because there were no requests logged"
                    )
        except psycopg2.Error as error:
            logging.error(
                "Failed to update testrun record (or events) with end time to Postgresql timescale database: "
                + repr(error)
            )
        logging.info(
            f"Report: {self.env.parsed_options.grafana_url}&var-testplan={self._testplan}&from={int(self._run_id.timestamp()*1000)}&to={int((end_time.timestamp()+1)*1000)}\n"
        )


class Print:
    """
    Print every response (useful when debugging a single locust)
    """

    def __init__(self, env: locust.env.Environment, include_length=False, include_time=False, include_context=False):
        env.events.request.add_listener(self.on_request)

        self.include_length = "length\t" if include_length else ""
        self.include_time = "time                    \t" if include_time else ""
        self.include_context = "context\t" if include_context else ""
        print(
            f"\n{self.include_time}type\t{'name'.ljust(50)}\tresp_ms\t{self.include_length}exception\t{self.include_context}"
        )

    def on_request(
        self, request_type, name, response_time, response_length, exception, context: dict, start_time=None, **_kwargs
    ):
        if exception:
            if isinstance(exception, CatchResponseError):
                e = str(exception)
            else:
                try:
                    e = repr(exception)
                except AttributeError:
                    e = f"{exception.__class__} (and it has no string representation)"
            errortext = e[:500].replace("\n", " ")
        else:
            errortext = ""
        if not context:
            context = ""

        if response_time is None:
            response_time = -1
        n = name.ljust(30) if name else ""

        if self.include_time:
            if start_time:
                print_t(datetime.fromtimestamp(start_time, tz=timezone.utc))
            else:
                print_t(datetime.now())

        print_t(request_type)
        print_t(n.ljust(50))
        print_t(str(round(response_time)).ljust(7))

        if self.include_length:
            print_t(response_length)

        print_t(errortext.ljust(9))

        if self.include_context:
            print_t(context)

        print()


class RescheduleTaskOnFail:
    def __init__(self, env: locust.env.Environment):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        env.events.request.add_listener(self.request)

    def request(self, exception, **_kwargs):
        if exception:
            raise RescheduleTask()


class InterruptTaskOnFail:
    def __init__(self, env: locust.env.Environment):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        env.events.request.add_listener(self.request)

    def request(self, exception, **_kwargs):
        if exception:
            raise InterruptTaskSet()


class StopUserOnFail:
    def __init__(self, env: locust.env.Environment):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        env.events.request.add_listener(self.request)

    def request(self, exception, **_kwargs):
        if exception:
            raise StopUser()


class ExitOnFail:
    def __init__(self, env: locust.env.Environment):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        env.events.request.add_listener(self.request)

    def request(self, exception, **_kwargs):
        if exception:
            gevent.sleep(0.2)  # wait for other listeners output to flush / write to db
            os._exit(1)


class QuitOnFail:
    def __init__(self, env: locust.env.Environment, name=None):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        self.name = name
        self.env = env
        env.events.request.add_listener(self.request)

    def request(self, exception, name, **_kwargs):
        if exception and (name == self.name or not self.name):
            gevent.sleep(0.2)  # wait for other listeners output to flush / write to db
            self.env.runner.quit()


def is_worker():
    return "--worker" in sys.argv


def is_master():
    return "--master" in sys.argv


class TimescaleListener:
    def __init__(self, *args, **kwargs):
        raise Exception("All listeners have had their -Listener suffix removed, please update your code.")


class RescheduleTaskOnFailListener:
    def __init__(self, *args, **kwargs):
        raise Exception("All listeners have had their -Listener suffix removed, please update your code.")

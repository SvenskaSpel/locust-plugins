from contextlib import contextmanager
from locust.exception import (
    RescheduleTask,
    StopUser,
    CatchResponseError,
    InterruptTaskSet,
)  # need to do this first to make sure monkey patching is done
import locust.env
import gevent
from gevent.lock import Semaphore
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
from typing import Callable, List


# pylint: disable=trailing-whitespace # pylint is confused by multiline strings used for SQL


def safe_serialize(obj):
    def default(o):
        return f"<<non-serializable: {type(o).__qualname__}>>"

    return json.dumps(obj, default=default)


def print_t(s):
    print(str(s), end="\t")


class Timescale:  # pylint: disable=R0902
    """
    See timescale_listener_ex.py for documentation
    """

    dblock = Semaphore()
    first_instance = True

    def __init__(self, env: locust.env.Environment):
        if not Timescale.first_instance:
            # we should refactor this into a module as it is much more pythonic
            raise Exception(
                "You tried to initialize the Timescale listener twice, maybe both in your locustfile and using command line --timescale? Ignoring second initialization."
            )
        Timescale.first_instance = False
        self.env = env
        self._samples: List[dict] = []
        self._background = gevent.spawn(self._run)
        self._hostname = socket.gethostname()  # pylint: disable=no-member
        self._username = os.getenv("USER", "unknown")
        self._finished = False
        self._pid = os.getpid()
        events = self.env.events
        events.test_start.add_listener(self.on_test_start)
        events.request.add_listener(self.on_request)
        events.cpu_warning.add_listener(self.on_cpu_warning)
        events.quit.add_listener(self.on_quit)
        events.spawning_complete.add_listener(self.spawning_complete)
        atexit.register(self.log_stop_test_run)

        if self.env.runner is not None:
            self.env.runner.register_message("run_id", self.set_run_id)

    def set_run_id(self, environment, msg, **kwargs):
        logging.debug(f"run id from master: {msg.data}")
        self._run_id = datetime.strptime(msg.data, "%Y-%m-%d, %H:%M:%S.%f").replace(tzinfo=timezone.utc)

    @contextmanager
    def dbcursor(self):
        with self.dblock:
            try:
                if self.dbconn.closed:
                    self.dbconn = self._dbconn()
                yield self.dbconn.cursor()
            except psycopg2.Error:
                try:
                    # try to recreate connection
                    self.dbconn = self._dbconn()
                except:
                    pass
                raise

    def on_cpu_warning(self, environment: locust.env.Environment, cpu_usage, message=None, timestamp=None, **kwargs):
        # passing a custom message & timestamp to the event is a haxx to allow using this event for reporting generic events
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()
        if not message:
            message = f"{self._testplan} High CPU usage ({cpu_usage}%)"
        with self.dbcursor() as cur:
            cur.execute("INSERT INTO events (time, text) VALUES (%s, %s)", (timestamp, message))

    def set_gitrepo(self):
        self._gitrepo = None
        try:
            path = os.getcwd()
            while not self._gitrepo and len(path) > 4:
                try:
                    with open(path + "/.git/config", "r") as f:
                        for l in f.readlines():
                            l = l.strip()
                            if l.startswith("url ="):
                                self._gitrepo = l.split(":")[1][:-4]
                                return
                except FileNotFoundError:
                    pass
                path = os.path.abspath(os.path.dirname(path))
        except:
            pass  # probably on windows or something
        logging.debug("couldnt figure out which git repo your locustfile is in")

    def on_test_start(self, environment: locust.env.Environment):
        # set _testplan from here, because when running distributed, override_test_plan is not yet available at init time
        self._testplan = self.env.parsed_options.override_plan_name or self.env.parsed_options.locustfile
        try:
            self.dbconn = self._dbconn()
        except psycopg2.OperationalError as e:
            logging.error(e)
            sys.exit(1)
        self.set_gitrepo()

        if not self.env.parsed_options.worker:
            self._run_id = datetime.now(timezone.utc)
            logging.info(
                f"Follow test run here: {self.env.parsed_options.grafana_url}&var-testplan={self._testplan}&from={int(self._run_id.timestamp()*1000)}&to=now"
            )
            msg = self._run_id.strftime("%Y-%m-%d, %H:%M:%S.%f")
            if environment.runner is not None:
                logging.debug(f"about to send run_id to workers: {msg}")
                environment.runner.send_message("run_id", msg)
            self.log_start_testrun()
            self._user_count_logger = gevent.spawn(self._log_user_count)

    def _dbconn(self) -> psycopg2.extensions.connection:
        try:
            conn = psycopg2.connect(
                host=self.env.parsed_options.pghost,
                user=self.env.parsed_options.pguser,
                password=self.env.parsed_options.pgpassword,
                database=self.env.parsed_options.pgdatabase,
                port=self.env.parsed_options.pgport,
                keepalives_idle=120,
                keepalives_interval=20,
                keepalives_count=6,
            )
        except Exception:
            logging.error(
                "Could not connect to postgres. Use standard postgres env vars or --pg* command line options to specify where to report locust samples (https://www.postgresql.org/docs/13/libpq-envars.html)"
            )
            raise
        conn.autocommit = True
        return conn

    def _log_user_count(self):
        while True:
            if self.env.runner is None:
                return  # there is no runner, so nothing to log...
            try:
                with self.dbcursor() as cur:
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
            with self.dbcursor() as cur:
                psycopg2.extras.execute_values(
                    cur,
                    """INSERT INTO request(time,run_id,greenlet_id,loadgen,name,request_type,response_time,success,testplan,response_length,exception,pid,url,context) VALUES %s""",
                    samples,
                    template="(%(time)s, %(run_id)s, %(greenlet_id)s, %(loadgen)s, %(name)s, %(request_type)s, %(response_time)s, %(success)s, %(testplan)s, %(response_length)s, %(exception)s, %(pid)s, %(url)s, %(context)s)",
                )

        except psycopg2.Error as error:
            logging.error("Failed to write samples to Postgresql timescale database: " + repr(error))
            sys.exit(1)

    def on_quit(self, exit_code, **kwargs):
        self._finished = True
        atexit._clear()  # make sure we dont capture additional ctrl-c:s # pylint: disable=protected-access
        self._background.join(timeout=10)
        if getattr(self, "_user_count_logger", False):
            self._user_count_logger.kill()
        self.log_stop_test_run(exit_code)

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
        **kwargs,
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
        cmd = sys.argv
        del cmd[0]
        with self.dbcursor() as cur:
            cur.execute(
                "INSERT INTO testrun (id, testplan, num_clients, rps, description, env, profile_name, username, gitrepo, changeset_guid, arguments) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    self._run_id,
                    self._testplan,
                    self.env.parsed_options.num_users or 1,
                    self.env.parsed_options.ips,  # this field is incorrectly called "rps" in db, it should be called something like "target_ips"
                    self.env.parsed_options.description,
                    self.env.parsed_options.test_env,
                    self.env.parsed_options.profile,
                    self._username,
                    self._gitrepo,
                    self.env.parsed_options.test_version,
                    " ".join(cmd),
                ),
            )
            cur.execute(
                "INSERT INTO events (time, text) VALUES (%s, %s)",
                (datetime.now(timezone.utc).isoformat(), self._testplan + " started by " + self._username),
            )

    def spawning_complete(self, user_count):
        if not self.env.parsed_options.worker:  # only log for master/standalone
            end_time = datetime.now(timezone.utc)
            try:
                with self.dbcursor() as cur:
                    cur.execute(
                        "INSERT INTO events (time, text) VALUES (%s, %s)",
                        (end_time, f"{self._testplan} rampup complete, {user_count} users spawned"),
                    )
            except psycopg2.Error as error:
                logging.error(
                    "Failed to insert rampup complete event time to Postgresql timescale database: " + repr(error)
                )

    def log_stop_test_run(self, exit_code=None):
        logging.debug(f"Test run id {self._run_id} stopping")
        if self.env.parsed_options.worker:
            return  # only run on master or standalone
        if getattr(self, "dbconn", None) is None:
            return  # test_start never ran, so there's not much for us to do
        end_time = datetime.now(timezone.utc)
        try:
            with self.dbcursor() as cur:
                cur.execute(
                    "UPDATE testrun SET end_time = %s, exit_code = %s where id = %s",
                    (end_time, exit_code, self._run_id),
                )
                cur.execute(
                    "INSERT INTO events (time, text) VALUES (%s, %s)",
                    (end_time, self._testplan + f" finished with exit code: {exit_code}"),
                )
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
                    logging.info(
                        "Got DivisionByZero error when trying to update testrun, most likely because there were no requests logged"
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
        self, request_type, name, response_time, response_length, exception, context: dict, start_time=None, **kwargs
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

    def request(self, exception, **kwargs):
        if exception:
            raise RescheduleTask(exception)


class InterruptTaskOnFail:
    def __init__(self, env: locust.env.Environment):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        env.events.request.add_listener(self.request)

    def request(self, exception, **kwargs):
        if exception:
            raise InterruptTaskSet()


class StopUserOnFail:
    def __init__(self, env: locust.env.Environment):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        env.events.request.add_listener(self.request)

    def request(self, exception, **kwargs):
        if exception:
            raise StopUser()


class ExitOnFail:
    def __init__(self, env: locust.env.Environment):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        env.events.request.add_listener(self.request)

    def request(self, exception, **kwargs):
        if exception:
            gevent.sleep(0.2)  # wait for other listeners output to flush / write to db
            sys.exit(1)


class QuitOnFail:
    def __init__(self, env: locust.env.Environment, name=None):
        # make sure to add this listener LAST, because any failures will throw an exception,
        # causing other listeners to be skipped
        self.name = name
        self.env = env
        env.events.request.add_listener(self.request)

    def request(self, exception, name, **kwargs):
        if exception and (name == self.name or not self.name):
            gevent.sleep(0.2)  # wait for other listeners output to flush / write to db
            self.env.runner.quit()


class RunOnFail:
    def __init__(self, env: locust.env.Environment, function: Callable):
        # execute the provided function on failure
        self.function = function
        env.events.request.add_listener(self.request)

    def request(self, exception, **kwargs):
        if exception:
            self.function(exception, **kwargs)


class RunOnUserError:
    def __init__(self, env: locust.env.Environment, function: Callable):
        # execute the provided function on unhandled exception in a task
        self.function = function
        env.events.user_error.add_listener(self.user_error)

    def user_error(self, user_instance, exception, tb, **kwargs):
        if exception:
            self.function(user_instance, exception, tb, **kwargs)

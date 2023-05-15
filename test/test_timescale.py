from unittest import TestCase
from time import sleep
import subprocess
import logging
from subprocess import PIPE
from tempfile import NamedTemporaryFile
from contextlib import contextmanager
import os
import textwrap
import signal
import atexit

logging.getLogger().setLevel(logging.DEBUG)


@contextmanager
def temporary_file(content, suffix="_locustfile.py", dir=None):
    f = NamedTemporaryFile(suffix=suffix, delete=False, dir=dir)
    f.write(content.encode("utf-8"))
    f.close()
    try:
        yield f.name
    finally:
        if os.path.exists(f.name):
            os.remove(f.name)


class TestTimescale(TestCase):
    def test_distributed_timescale_listener(self):
        with temporary_file(
            content=textwrap.dedent(
                """
            from locust import User, task, constant, events
            import locust_plugins
            class TestUser(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    self.environment.events.request.fire(
                        request_type="GET",
                        name="/test",
                        response_time=666,
                        response_length=1337,
                        exception=None,
                        context={},
                    )
        """
            )
        ) as file_path:
            master = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    file_path,
                    "--timescale",
                    "--master",
                    "--exit-code-on-error",
                    "0",
                    "--headless",
                    "-u",
                    "10",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            worker1 = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    file_path,
                    "--timescale",
                    "--worker",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            sleep(2)
            worker2 = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    file_path,
                    "--timescale",
                    "--worker",
                    "-L",
                    "DEBUG",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            sleep(2)

            def cleanup():
                master.kill()
                worker2.kill()
                worker1.kill()

            # ensure we dont leave behind any subprocesses even if test fails
            atexit.register(cleanup)

            master.send_signal(signal.SIGTERM)
            stdout, stderr = master.communicate()
            self.assertIn("Starting Locust", stderr)
            self.assertIn("Shutting down (exit code 0)", stderr)
            self.assertIn("Follow test run ", stderr)
            self.assertEqual(0, master.returncode)

            stdout, stderr = worker1.communicate()
            self.assertNotIn("Unknown message type", stderr)
            self.assertIn("Starting Locust", stderr)
            self.assertIn("Shutting down (exit code 0)", stderr)
            self.assertEqual(0, worker1.returncode)

            # this is the real test
            stdout, stderr = worker2.communicate()
            self.assertNotIn("Unknown message type", stderr)  # init didnt happen/happened after run_id got sent?
            self.assertNotIn("DivisionByZero", stderr)  # rebalancing never happened?
            self.assertIn("received run_id", stderr)
            print(stderr)
            self.assertEqual(0, worker2.returncode)

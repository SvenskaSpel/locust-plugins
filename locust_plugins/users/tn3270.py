# Wrapper for Telnet 3270 sessions
# Author: Adam Munawar Rahman (github.com/msradam)

from py3270 import Emulator
from locust import User
import time


class tn3270User(User):
    abstract = True

    def __init__(self, environment):
        super().__init__(environment)
        self.client = tn3270Client(environment=environment)


class tn3270Client:
    def __init__(self, environment):
        self.environment = environment
        self.emulator = None
        self.host = None

    def connect(self, user=None, password=None, port=23, timeout=30, trace=False, tracefile=None):
        self.user = user
        self.password = password
        self.port = port
        self.timeout = timeout
        self.tracefile = tracefile

        start_perf_counter = time.perf_counter()
        exception = None
        response = ""

        try:
            if trace:
                self.emulator = Emulator(
                    visible=False, timeout=self.timeout, args=["-trace", "-tracefile", self.tracefile]
                )
            else:
                self.emulator = Emulator(visible=False, timeout=self.timeout)

            self.emulator.connect(f"y:{self.environment.host}:{self.port}")
            # Wait briefly for screen to populate
            self.emulator.wait_for_field()
            # Get actual screen content as response
            c = self.emulator.exec_command(b"Ascii()")
            response = b"\n".join(c.data).decode()
        except Exception as e:
            exception = e

        response_time = (time.perf_counter() - start_perf_counter) * 1000

        if exception:
            self.environment.events.request.fire(
                request_type="tn3270",
                request_method="connect",
                name=f"connect:{self.environment.host}:{port}",
                exception=exception,
                response_time=response_time,
                response_length=len(str(exception)),
            )
            raise exception

        self.environment.events.request.fire(
            request_type="tn3270",
            request_method="connect",
            name=f"connect:{self.environment.host}:{port}",
            response_time=response_time,
            response_length=len(response),
        )

    def string_wait(self, string):
        try:
            while True:
                self.emulator.wait_for_field()
                c = self.emulator.exec_command(b"Ascii()")
                screen_text = b"\n".join(c.data).decode()
                if string in screen_text:
                    return screen_text
        except Exception as e:
            raise e

    def send_command(self, command, wait_for_response=True):
        start_perf_counter = time.perf_counter()
        exception = None
        response = ""

        try:
            self.emulator.send_string(command)
            self.emulator.send_enter()

            if wait_for_response:
                self.emulator.wait_for_field()
                c = self.emulator.exec_command(b"Ascii()")
                response = b"\n".join(c.data).decode()
        except Exception as e:
            exception = e

        response_time = (time.perf_counter() - start_perf_counter) * 1000

        if exception:
            self.environment.events.request.fire(
                request_type="tn3270",
                request_method="command",
                name=f"send_command:{command[:30]}",  # Use first 30 chars of command as name
                exception=exception,
                response_time=response_time,
                response_length=len(str(exception)),
            )
            raise exception

        self.environment.events.request.fire(
            request_type="tn3270",
            request_method="command",
            name=f"send_command:{command[:30]}",
            response_time=response_time,
            response_length=len(response),
        )
        return response

    def wait_for_field(self):
        try:
            self.emulator.wait_for_field()
        except Exception as e:
            raise e

    def send_pf(self, key_number, wait_for_response=True):
        """Send PF key and measure response time"""
        start_perf_counter = time.perf_counter()
        exception = None
        response = ""

        try:
            if 1 <= key_number <= 24:
                method = getattr(self.emulator, f"send_pf{key_number}")
                method()

                if wait_for_response:
                    self.emulator.wait_for_field()
                    c = self.emulator.exec_command(b"Ascii()")
                    response = b"\n".join(c.data).decode()
            else:
                raise ValueError(f"Invalid PF key number: {key_number}. Must be between 1 and 24.")
        except Exception as e:
            exception = e

        response_time = (time.perf_counter() - start_perf_counter) * 1000

        if exception:
            self.environment.events.request.fire(
                request_type="tn3270",
                request_method="pf_key",
                name=f"send_pf{key_number}",
                exception=exception,
                response_time=response_time,
                response_length=len(str(exception)),
            )
            raise exception

        self.environment.events.request.fire(
            request_type="tn3270",
            request_method="pf_key",
            name=f"send_pf{key_number}",
            response_time=response_time,
            response_length=len(response),
        )
        return response

    def get_screen_text(self):
        """Get current screen text"""
        try:
            c = self.emulator.exec_command(b"Ascii()")
            return b"\n".join(c.data).decode()
        except Exception as e:
            raise e

    def disconnect(self):
        self.emulator.terminate()

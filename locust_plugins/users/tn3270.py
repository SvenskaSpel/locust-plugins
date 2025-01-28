# Wrapper for Telnet 3270 sessions
# Author: Adam Munawar Rahman (github.com/msradam)

from py3270 import Emulator
from locust import User


class tn3270User(User):
    abstract = True

    def __init__(self, environment):
        super().__init__(environment)
        self.client = tn3270Client(environment=environment)


class tn3270Client:
    def __init__(self, environment):
        self.environment = environment
        self.emulator = None

    def connect(self, user=None, password=None, port=23, timeout=30, trace=False, tracefile=None):
        self.user = user
        self.password = password
        self.port = port
        self.timeout = timeout
        self.tracefile = tracefile
        if trace:
            self.emulator = Emulator(visible=False, timeout=self.timeout, args=["-trace", "-tracefile", self.tracefile])
        else:
            self.emulator = Emulator(visible=False, timeout=self.timeout)
        self.emulator.connect("y:%s:%d" % (self.environment.host, self.port))

    def string_wait(self, string):
        while True:
            self.emulator.wait_for_field()
            c = self.emulator.exec_command(b"Ascii()")
            if string in b"\n".join(c.data).decode():
                return

    def disconnect(self):
        self.emulator.terminate()

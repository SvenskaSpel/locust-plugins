from locust import task
from locust_plugins.users.tn3270 import tn3270User
from pprint import pprint


class DemoTn3270User(tn3270User):
    """
    Demo of 3270 connection functionality,
    the demo user initiates a telnet connection to telehack.com,
    a simulation of an ARPANET / Usenet interface which hosts
    several terminal based application

    Once the user accesses Telehack, they select the cowsay app,
    the main task repeatedly sends requests to cowsay,
    the emulator terminates once the Locust session ends
    """

    def on_start(self):
        self.environment.host = "telehack.com"
        self.client.connect()
        self.client.emulator.wait_for_field()
        self.client.string_wait("Type NEWUSER to create an account.")
        self.client.emulator.wait_for_field()
        self.client.emulator.send_string("cowsay")
        self.client.emulator.send_enter()

    @task
    def run_command(self):
        self.client.emulator.wait_for_field()
        self.client.emulator.send_string("cowsay hello")
        self.client.emulator.wait_for_field()
        # Pretty prints the current screen
        pprint(self.client.emulator.exec_command("PrintText(string)").data)

    def on_stop(self):
        self.client.disconnect()

from locust import task, between
from locust_plugins.users.tn3270 import tn3270User


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

    wait_time = between(1, 3)  # Add realistic think time between actions

    def on_start(self):
        self.environment.host = "telehack.com"
        # Connect to the telnet server
        self.client.connect()
        # Wait for welcome screen
        self.client.string_wait("Type NEWUSER to create an account.")
        # Navigate to cowsay application
        self.client.wait_for_field()
        self.client.send_command("cowsay")

    @task(3)
    def run_cowsay_command(self):
        self.client.send_command("cowsay hello from locust")

    @task(2)
    def run_simple_cowsay(self):
        self.client.send_command("cowsay moo")

    @task(1)
    def run_complex_cowsay(self):
        self.client.send_command("cowsay -f tux complex hello!")

    def on_stop(self):
        self.client.disconnect()

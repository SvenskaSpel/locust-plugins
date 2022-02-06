from locust_plugins.users.playwright import PlaywrightUser
from locust import events, run_single_user, task
from locust_plugins import listeners
import asyncio
import gevent
import os


class DemoUser(PlaywrightUser):
    script = "playwright-recording.py"


@events.quitting.add_listener
def on_locust_quit(environment, **_kwargs):
    # Playwright outputs control codes that alter the terminal, so we need to reset it
    os.system("reset")


if __name__ == "__main__":
    # enable easy debugging from VS Code
    run_single_user(DemoUser)

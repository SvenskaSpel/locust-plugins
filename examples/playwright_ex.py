import time
import os

from locust import events, run_single_user
from locust_plugins.users.playwright import PlaywrightUser
from playwright.async_api import Playwright


class ScriptedBased(PlaywrightUser):
    # run a script that you recorded in playwright, exported as Python Async
    script = "playwright-recording.py"


class Advanced(PlaywrightUser):
    browser = None
    # PlaywrightUser doesnt currently support multiple tasks, they all just run this method
    # do not use the @task on another method, it will not work!
    async def task(self, playwright: Playwright):
        if not self.browser:
            self.browser = await playwright.chromium.launch(
                headless=(__name__ != "__main__"),
                handle_sigint=False,
            )
        context = await self.browser.new_context()
        page = await context.new_page()
        start_time = time.time()
        start_perf_counter = time.perf_counter()
        await page.goto("https://www.google.com/")
        self.environment.events.request.fire(
            request_type="GOTO",
            name="google",
            start_time=start_time,
            response_time=(time.perf_counter() - start_perf_counter) * 1000,
            response_length=0,
            context={},
            exception=None,
        )
        await context.close()


@events.quitting.add_listener
def on_locust_quit(environment, **_kwargs):
    # Playwright outputs control codes that alter the terminal, so we need to reset it
    os.system("reset")


if __name__ == "__main__":
    run_single_user(Advanced)

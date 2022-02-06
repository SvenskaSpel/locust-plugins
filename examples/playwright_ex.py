from locust_plugins.users.playwright import PlaywrightUser
from locust import events, run_single_user
import os
from playwright.async_api import Playwright
import time


class ScriptedBased(PlaywrightUser):
    # run a script that you recorded in playwright, exported as Python Async
    script = "playwright-recording.py"


class Advanced(PlaywrightUser):
    # PlaywrightUser doesnt currently support multiple tasks, they all just run t
    async def task(self, playwright: Playwright):
        browser = await playwright.chromium.launch(headless=False, handle_sigint=False)
        context = await browser.new_context()
        page = await context.new_page()
        start_time = time.time()
        start_perf_counter = time.perf_counter()
        await page.goto("https://www.google.com/")
        self.environment.events.request.fire(
            request_type="request",
            name="google_loaded",
            start_time=start_time,
            response_time=(time.perf_counter() - start_perf_counter) * 1000,
            response_length=0,
            context={},
            exception=None,
        )
        await context.close()
        await browser.close()


@events.quitting.add_listener
def on_locust_quit(environment, **_kwargs):
    # Playwright outputs control codes that alter the terminal, so we need to reset it
    os.system("reset")


if __name__ == "__main__":
    run_single_user(ScriptedBased)

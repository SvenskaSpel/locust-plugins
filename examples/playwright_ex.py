# Demonstrates the two ways to run Playwright
# Dont forget to first install the browsers by running: playwright install

import time
from locust import run_single_user, task
from locust_plugins.users.playwright import PlaywrightUser, PlaywrightScriptUser, pw


class ScriptedBased(PlaywrightScriptUser):
    # run a script that you recorded in playwright, exported as Python Async
    script = "playwright-recording.py"


class Advanced(PlaywrightUser):
    @task
    @pw
    async def google(self):
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


if __name__ == "__main__":
    run_single_user(Advanced)

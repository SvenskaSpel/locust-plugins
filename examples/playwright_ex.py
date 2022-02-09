# Demonstrates the two ways to run Playwright
# Dont forget to first install the browsers by running: playwright install

import time
from locust import run_single_user, task
from locust_plugins.users.playwright import PlaywrightUser, PlaywrightScriptUser, pw, event


class ScriptedBased(PlaywrightScriptUser):
    # run a script that you recorded in playwright, exported as Python Async
    script = "playwright-recording.py"


class Advanced(PlaywrightUser):
    @task
    @pw
    async def google(self):
        async with event(self, "Load up google"):  # log this as an event
            await self.page.goto("https://www.google.com/")  # load a page

        async with event(self, "Approve terms and conditions"):
            async with self.page.expect_navigation(wait_until="domcontentloaded"):
                await self.page.click('button:has-text("Jag godkänner")')  # Click "I approve" in swedish...


if __name__ == "__main__":
    run_single_user(Advanced)

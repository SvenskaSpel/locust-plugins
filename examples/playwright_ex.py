# Demonstrates the two ways to run Playwright (prerecorded script or "manual")

# Notes:
# Dont forget to first install the browsers by running: playwright install
# Browsers are heavy. Dont expect to be able to do as much load as usual with Locust. Optimize your tests by blocking requests for unnecessary resources.
# Dont run too many users per worker instance (or you'll get the dreaded "CPU usage over 90%" warning). Instead, scale using more Locust workers. This is made easy by using locust-swarm.
# It is easy to accidentally make Playwright tests stall for a long time, for example if your page does finish loading completely (triggering the "load" event). Experiment with alternative wait strategies (e.g. wait_until="domcontentloaded" or self.page.wait_for_selector(...))

from locust import run_single_user, task
from locust_plugins.users.playwright import PlaywrightUser, PlaywrightScriptUser, pw, event


class ScriptedBased(PlaywrightScriptUser):
    # run a script that you recorded in playwright, exported as Python Async
    script = "playwright-recording.py"


class Manual(PlaywrightUser):
    @task
    @pw
    async def google(self):
        async with event(self, "Load up google"):  # log this as an event
            await self.page.goto("https://www.google.com/")  # load a page

        async with event(self, "Approve terms and conditions"):
            async with self.page.expect_navigation(wait_until="domcontentloaded"):
                await self.page.click('button:has-text("Jag godkänner")')  # Click "I approve" in swedish...


if __name__ == "__main__":
    run_single_user(Manual)

# You need to start selenium server first:
# Download it from https://www.seleniumhq.org/download/ and run it by executing:
# java -jar selenium-server-4.0.0-beta-4.jar standalone
# Also, make sure you have installed chromedriver first. On macOS you would do: brew install --cask chromedriver
import time
from locust import task, constant, events
from locust_plugins import run_single_user
from locust_plugins.users import WebdriverUser
from locust_plugins.listeners import RescheduleTaskOnFail
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class MyUser(WebdriverUser):
    wait_time = constant(2)

    if __name__ == "__main__":
        # wait a bit at the end to make debugging easier
        wait_time = constant(5)
    else:
        # headless by default if running real locust and not just debugging
        headless = True

    def on_start(self):
        self.client.set_window_size(1400, 1000)
        self.client.implicitly_wait(5)

    # this is just an example, but it shows off some of the things you might want to do in a Webdriver test
    @task
    def my_task(self):
        self.clear()
        self.client.start_time = time.monotonic()  # to measure the time from now to first find_element finishes
        scenario_start_time = self.client.start_time  # to measure the time for the whole scenario
        self.client.get("https://spela.test4.svenskaspel.se/")
        self.client.add_cookie(
            {
                "name": "cookie_consent",
                "value": '{"ad":true,"personalized":true,"version":0}',
                "path": "/",
                "secure": True,
            }
        )
        self.client.get("https://spela.test4.svenskaspel.se/logga-in/bankid/ssn")
        ssn_input = self.client.find_element(By.CSS_SELECTOR, "#ssn", name="ssn entry page ready")
        ssn_input.click()
        ssn_input.send_keys("199901010109")
        ssn_input.send_keys(Keys.RETURN)
        self.client.implicitly_wait(10)
        self.client.find_element(By.XPATH, '//*[@id="last-login-time"]/div/div[4]/a/span', name="logged in").click()
        self.client.find_element(
            By.CSS_SELECTOR,
            "body > div.fixed-top-content.js-top-content-wrapper.balance-bar-ao-brand-small > div.balance-bar-account > span.balance-bar-account-item.balance-bar-left-border.pointer.js-balance-toggle.balance-bar-toggle > span",
            name="balance clickable",  # this is just client side so it will be really fast
        ).click()

        self.environment.events.request.fire(
            request_type="flow",
            name="log in flow",
            response_time=(time.monotonic() - scenario_start_time) * 1000,
            response_length=0,
            exception=None,
        )


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    RescheduleTaskOnFail(environment)


if __name__ == "__main__":
    run_single_user(MyUser, init_listener=on_locust_init)

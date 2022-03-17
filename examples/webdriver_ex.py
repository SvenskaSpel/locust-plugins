# You need to start selenium server first:
# Download it from https://www.seleniumhq.org/download/ and run it by executing:
# java -jar selenium-server-4.0.0-beta-4.jar standalone
# Also, make sure you have installed chromedriver first. On macOS you would do: brew install --cask chromedriver
#
# You can also run selnium server via docker using the following example command:
# docker run -e SE_NODE_SESSION_TIMEOUT=60 -e SE_NODE_MAX_SESSIONS=5 -p 4444:4444 -p 7900:7900 --shm-size="2g" --rm selenium/standalone-chrome:96.0
import time
from locust import task, constant, events, run_single_user
from locust_plugins.users import WebdriverUser
from locust_plugins.listeners import RescheduleTaskOnFail
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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
        self.client.start_time = time.monotonic()  # to measure the time from now to first locust_find_element finishes
        scenario_start_time = self.client.start_time  # to measure the time for the whole scenario
        self.client.get("https://example.com/")
        self.client.add_cookie(
            {
                "name": "cookie_consent",
                "value": '{"ad":true,"personalized":true,"version":0}',
                "path": "/",
                "secure": True,
            }
        )
        self.client.get("https://example.com/")
        ssn_input = self.client.locust_find_element(By.CSS_SELECTOR, "#ssn", name="ssn entry page ready")
        ssn_input.click()
        ssn_input.send_keys("199901010109")
        ssn_input.send_keys(Keys.RETURN)
        self.client.implicitly_wait(10)
        self.client.locust_find_element(
            By.XPATH, '//*[@id="last-login-time"]/div/div[4]/a/span', name="logged in"
        ).click()
        self.client.locust_find_element(
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

    @task
    def failure_with_context_manager(self):
        # The context manager tracks all activities together under a single event with the time based on
        # the entry into the with loop, and finishes when the exist occurs, or success/failure method is called.
        # Don't call success/failure multiple times - create a new context or task if you need to track multiple events.
        with self.request(name="failure_with_context_manager") as request:
            request.client.get("https://example.com/")

            # Leverate native webdriver features like Wait
            wait = WebDriverWait(self.client, 5, poll_frequency=0.5)
            # This will cause a timeout because #ssn does not exist on the example.com page.
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#ssn")))

            # If success/failure is called automatically based on if an exception is raised from the content of the context.
            # You can also manually trigger success/failure if needed.
            # request.success()
            # or
            # request.failure(exception)

    @task
    def failure_with_context_manager2(self):
        # Example of how a element not on the page generates a failure
        with self.request(name="failure_with_context_manager2") as request:
            request.client.get("https://example.com/")

            # simple check for element presence -> raises no_such_element exception which is caught by the context manager.
            request.client.find_element(By.CSS_SELECTOR, "body > div > div")

    @task
    def success_with_context_manager(self):
        # Example of a successful lookup
        with self.request(name="success_with_context_manager") as request:
            request.client.get("https://example.com/")

            # leverage native webdriver features like Wait
            wait = WebDriverWait(self.client, 5, poll_frequency=0.5)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > div")))

    @task
    def example_with_context_manager(self):
        with self.request(name="example_with_context_manager") as request:
            request.client.get("https://example.com/")
            title = request.client.find_element(By.CSS_SELECTOR, "body > div > h1")
            if title.text == "Example Domain":
                request.success()
            else:
                request.failure("Page title didn't match")


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    RescheduleTaskOnFail(environment)


if __name__ == "__main__":
    run_single_user(MyUser)

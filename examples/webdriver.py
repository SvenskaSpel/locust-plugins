#!/usr/bin/env python3
# This is an example of how to use the WebdriverLocust
# You need to start selenium server first.
# Download it from https://www.seleniumhq.org/download/ and run it by executing:
# java -jar selenium-server-standalone-3.141.59.jar
from locust_plugins.debug import run_single_user
from locust_plugins.locusts import WebdriverLocust
from locust_plugins.postgresreader import PostgresReader

import os
import time
from locust import TaskSet, task
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

customer_reader = PostgresReader(f"env='{os.environ['LOCUST_TEST_ENV']}' AND tb=0 AND lb=1")


class UserBehaviour(TaskSet):
    def on_start(self):
        self.client.set_window_size(1400, 1000)
        self.client.implicitly_wait(10)

    @task
    def my_task(self):
        short_sleep = 1 if __name__ == "__main__" else 0.1
        # this is just an example, but it shows off some of the things you might want to do in a Webdriver test
        self.client.delete_all_cookies()
        customer = customer_reader.get()

        start_at = time.time()
        self.client.get(self.locust.host)
        try:
            self.client.find_element_by_css_selector(".btn-inverted").click()
        except NoSuchElementException:
            pass  # dont really care about this

        self.client.find_element_by_css_selector(".js-nav-list-item-link-login").click()
        time.sleep(short_sleep)
        self.client.find_element_by_xpath('//*[@id="bankidTab"]/button[1]').click()
        time.sleep(short_sleep)
        self.client.find_element_by_xpath('//*[@id="ssn"]')
        ssn = customer["ssn"]
        ssn_input = self.client.switch_to.active_element
        # Sometimes send_keys has issues due to client side javascript. This is a workaround.
        self.client.execute_script(
            "arguments[0].setAttribute('value', arguments[1])", ssn_input, ssn[:8] + "-" + ssn[-4:]
        )
        time.sleep(short_sleep)
        ssn_input.send_keys(Keys.RETURN)
        time.sleep(short_sleep)
        try:
            self.client.find_element_by_xpath('//*[@id="last-login-time"]/div/div[4]/a/span').click()
        except StaleElementReferenceException:
            # retry...
            self.client.find_element_by_xpath('//*[@id="last-login-time"]/div/div[4]/a/span').click()
        # typically you would release the customer only after its task has finished,
        # but in this case I dont care, and dont want to block another test run from using it
        # (particularly if this test crashes)
        customer_reader.release(customer)
        self.locust.environment.events.request_success.fire(
            request_type="Selenium", name="Log in", response_time=(time.time() - start_at) * 1000, response_length=0
        )
        time.sleep(short_sleep * 2)


class MyWebdriverLocust(WebdriverLocust):
    task_set = UserBehaviour
    min_wait = 0
    max_wait = 0
    host = f"https://spela.{os.environ['LOCUST_TEST_ENV']}.svenskaspel.se/"

    def __init__(self):
        super().__init__(headless=(__name__ != "__main__"))


if __name__ == "__main__":
    run_single_user(MyWebdriverLocust)

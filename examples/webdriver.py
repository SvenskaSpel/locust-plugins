#!/usr/bin/env python3
# This is an example of how to use the WebdriverLocust
# You need to start selenium server first.
# Download it from https://www.seleniumhq.org/download/ and run it by executing:
# java -jar selenium-server-standalone-3.141.59.jar
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()

from locust_plugins.locusts import WebdriverLocust
from locust_plugins.listeners import PrintListener
import time
from locust import TaskSet, task
from locust.events import request_success
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


class UserBehaviour(TaskSet):
    def on_start(self):
        self.client.set_window_size(1400, 1000)
        self.client.implicitly_wait(10)

    @task
    def my_task(self):
        # this is just an example, but it shows off some of the things you might want to do in a Webdriver test
        self.client.delete_all_cookies()
        start_at = time.time()
        self.client.get("https://example.com/")
        try:
            self.client.find_element_by_css_selector(".btn-inverted").click()
        except NoSuchElementException:
            pass  # dont really care about this
        self.client.find_element_by_css_selector(".js-nav-list-item-link-login").click()
        time.sleep(0.1)
        self.client.find_element_by_xpath('//*[@id="bankidTab"]/div[2]/button[1]').click()
        time.sleep(0.1)
        self.client.find_element_by_css_selector(
            "body > div.js-modal-container.modal-container.modal-animate-start.modal-container-login.modal-animate-started"
        )
        ssn = "299901019999"
        ssn_input = self.client.switch_to.active_element
        # Sometimes send_keys has issues due to client side javascript. This is a workaround.
        self.client.execute_script(
            "arguments[0].setAttribute('value', arguments[1])", ssn_input, ssn[:8] + "-" + ssn[-4:]
        )
        ssn_input.send_keys(Keys.RETURN)
        try:
            self.client.find_element_by_css_selector(
                "body > div.fixed-top-content.js-fixed-top-content > nav > ul > li.nav-list-item.nav-list-item-user.js-nav-list-item-user.js-nav-list-item.js-logged-in > a"
            ).click()
        except StaleElementReferenceException:
            # retry...
            self.client.find_element_by_css_selector(
                "body > div.fixed-top-content.js-fixed-top-content > nav > ul > li.nav-list-item.nav-list-item-user.js-nav-list-item-user.js-nav-list-item.js-logged-in > a"
            ).click()
        time.sleep(0.1)
        request_success.fire(
            request_type="Selenium", name="Logged in", response_time=(time.time() - start_at) * 1000, response_length=0
        )


class MyWebdriverLocust(WebdriverLocust):
    task_set = UserBehaviour
    min_wait = 0
    max_wait = 0


if __name__ == "__main__":
    PrintListener()
    MyWebdriverLocust().run()

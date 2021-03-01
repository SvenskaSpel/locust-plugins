# You need to start selenium server first:
# Download it from https://www.seleniumhq.org/download/ and run it by executing:
# java -jar selenium-server-4.0.0-beta-1.jar standalone
import time
from locust import task, constant, events
from locust_plugins import run_single_user
from locust_plugins.users import WebdriverUser
from locust_plugins.listeners import RescheduleTaskOnFail
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class MyUser(WebdriverUser):
    wait_time = constant(2)

    def __init__(self, parent):
        super().__init__(parent, headless=(__name__ != "__main__"))

    def on_start(self):
        self.client.set_window_size(1400, 1000)
        self.client.implicitly_wait(2)

    # this is just an example, but it shows off some of the things you might want to do in a Webdriver test
    @task
    def my_task(self):
        self.client.delete_all_cookies()
        self.client.start_time = time.time()
        self.client.get("https://spela.test4.svenskaspel.se/")
        self.client.add_cookie(
            {
                "name": "cookie_consent",
                "value": '{"ad":true,"personalized":true,"version":0}',
                "path": "/",
                "secure": True,
            }
        )
        start_at = time.monotonic()
        self.client.get("https://spela.test4.svenskaspel.se/logga-in/bankid/ssn")
        ssn_input = self.client.find_element(By.CSS_SELECTOR, "#ssn", name="ssn page ready")
        ssn_input.click()
        ssn_input.send_keys("199901010109")
        ssn_input.send_keys(Keys.RETURN)
        self.client.implicitly_wait(10)
        try:
            self.client.find_element(
                By.XPATH, '//*[@id="last-login-time"]/div/div[4]/a/span', name="login complete"
            ).click()
        except StaleElementReferenceException:
            # retry...
            self.client.find_element(
                By.XPATH, '//*[@id="last-login-time"]/div/div[4]/a/span', name="login complete"
            ).click()
        # show balance
        self.client.find_element(
            By.CSS_SELECTOR,
            "body > div.fixed-top-content.js-top-content-wrapper.balance-bar-ao-brand-small > div.balance-bar-account > span.balance-bar-account-item.balance-bar-left-border.pointer.js-balance-toggle.balance-bar-toggle > span",
            name="balance visible",
        ).click()

        self.environment.events.request_success.fire(
            request_type="Selenium",
            name="Log in",
            response_time=(time.monotonic() - start_at) * 1000,
            response_length=0,
        )


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    # make sure this is the last event handler you register, as later ones will not be triggered
    # if there is a failure
    RescheduleTaskOnFail(environment)


if __name__ == "__main__":
    run_single_user(MyUser, init_listener=on_locust_init)

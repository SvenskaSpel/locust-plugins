# See examples/webdriver_ex.py for more documentation
import subprocess
import time
from locust import User
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


class WebdriverClient(webdriver.Remote):
    def __init__(self, environment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._locust_environment = environment
        self.start_time = None

    def find_element(self, *args, name=None, **kwargs):  # pylint: disable=arguments-differ
        name = name or args[1]
        result = None
        if not self.start_time:
            self.start_time = time.time()
        try:
            result = super().find_element(*args, **kwargs)
        except Exception as e:
            total_time = int((time.time() - self.start_time) * 1000)
            self.start_time = None
            self._locust_environment.events.request_failure.fire(
                request_type="Selenium", name=name, response_time=total_time, exception=e.args[0], response_length=None
            )

            if not isinstance(e, WebDriverException):
                raise
        else:
            total_time = int((time.time() - self.start_time) * 1000)
            self.start_time = None
            self._locust_environment.events.request_success.fire(
                request_type="Selenium", name=name, response_time=total_time, response_length=None
            )

        return result


class WebdriverUser(User):

    abstract = True
    _first_instance = True

    def __init__(self, parent, headless=True):
        super().__init__(parent)
        if WebdriverUser._first_instance:
            WebdriverUser._first_instance = False
            # kill old webdriver browser instances
            subprocess.Popen(["killall", "chromedriver"])
            subprocess.Popen(["pkill", "-f", " --test-type=webdriver"])

        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        self.client = WebdriverClient(
            self.environment,
            command_executor="http://127.0.0.1:4444/wd/hub",
            desired_capabilities=chrome_options.to_capabilities(),
        )

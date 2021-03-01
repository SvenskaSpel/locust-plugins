# See examples/webdriver_ex.py for more documentation
import subprocess
import time
from locust import User
from locust.env import Environment
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options


class WebdriverClient(webdriver.Remote):
    def __init__(self, environment: Environment, headless: bool):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        super().__init__(desired_capabilities=chrome_options.to_capabilities())
        self.environment = environment
        self.start_time = None

    def find_element(self, *args, name=None, **kwargs):  # pylint: disable=arguments-differ
        name = name or args[1]
        result = None
        if not self.start_time:
            self.start_time = time.monotonic()
        try:
            result = super().find_element(*args, **kwargs)
        except Exception as e:
            total_time = (time.monotonic() - self.start_time) * 1000
            self.start_time = None
            error_message = e.args[0]
            try:
                if isinstance(e, NoSuchElementException):
                    implicit_wait_time = self.execute(webdriver.remote.command.Command.GET_TIMEOUTS)["value"][
                        "implicit"
                    ]
                    error_message = error_message.replace("Unable to locate element: ", "")
                    error_message = error_message.replace(
                        "\n  (Session info: ", f" (waited {implicit_wait_time/1000}s, "
                    )
            except:
                pass  # if this failed then we dont know how long we waited for, but it doesnt matter
            self.environment.events.request_failure.fire(
                request_type="find_element",
                name=name,
                response_time=total_time,
                exception=error_message,
                response_length=None,
            )

            if not isinstance(e, WebDriverException):
                raise
        else:
            total_time = (time.monotonic() - self.start_time) * 1000
            self.start_time = None
            self.environment.events.request_success.fire(
                request_type="find_element", name=name, response_time=total_time, response_length=None
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
            subprocess.Popen(["killall", "chromedriver"], stderr=subprocess.DEVNULL)
            subprocess.Popen(["pkill", "-f", " --test-type=webdriver"], stderr=subprocess.DEVNULL)

        self.client = WebdriverClient(self.environment, headless)

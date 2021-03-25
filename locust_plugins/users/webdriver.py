# See examples/webdriver_ex.py for more documentation
import subprocess
import time
from locust import User
from locust.env import Environment
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import greenlet
import datetime


class WebdriverClient(webdriver.Remote):
    def __init__(self, environment: Environment, headless: bool):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        capabilities = chrome_options.to_capabilities()
        # workaround for the first page being way to slow to load
        # ~2 minutes for my case (caused by some useless element being slow?)
        capabilities["pageLoadStrategy"] = "eager"
        super().__init__(desired_capabilities=capabilities)
        self.environment = environment
        self.start_time = None

    def clear_cache(self):
        self.command_executor._commands["SEND_COMMAND"] = ("POST", "/session/$sessionId/chromium/send_command")
        self.execute("SEND_COMMAND", dict(cmd="Network.clearBrowserCache", params={}))

    def find_element(self, by=By.ID, value=None, name=None, prefix=None, retry=0):  # pylint: disable=arguments-differ
        result = None
        if name and prefix:
            raise Exception("dont specify both name and prefix, that makes no sense")
        if not name:
            name = f"{prefix.ljust(13)} {by[0:5]} {value}"
        if not self.start_time:
            self.start_time = time.monotonic()
        try:
            result = super().find_element(by=by, value=value)
        except Exception as e:
            if retry < 2:
                return self.find_element(by=by, value=value, name=name, retry=retry + 1)
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
                pass  # if this failed then we dont know how long the implicit wait time was, but it doesnt matter
            timestring = datetime.datetime.now().replace(microsecond=0).isoformat().replace(":", ".")
            greenlet_id = getattr(greenlet.getcurrent(), "minimal_ident", 0)  # if we're debugging there is no greenlet
            self.save_screenshot(
                f"{timestring}_{name.replace(' ', '_').replace('{','_').replace('}','_').replace(':','_')}_{greenlet_id}.png"
            )
            self.environment.events.request_failure.fire(
                request_type="find",
                name=name,
                response_time=total_time,
                exception=error_message,
                response_length=0,
            )
            if not isinstance(e, WebDriverException):
                raise
        else:
            total_time = (time.monotonic() - self.start_time) * 1000
            self.start_time = None
            self.environment.events.request_success.fire(
                request_type="find", name=name, response_time=total_time, response_length=0
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

    def on_stop(self):
        self.client.close()

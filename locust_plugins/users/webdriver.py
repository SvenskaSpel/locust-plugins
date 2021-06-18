# See examples/webdriver_ex.py for more documentation
import subprocess
import time
from locust import User
from locust.env import Environment
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, InvalidSessionIdException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import greenlet
import datetime


class WebdriverClient(webdriver.Remote):
    def __init__(self, environment: Environment, headless: bool):
        options = Options()
        self.headless = headless
        options.headless = self.headless
        for arg in [
            "--disable-translate",
            "--disable-extensions",
            "--disable-background-networking",
            "--safebrowsing-disable-auto-update",
            "--disable-sync",
            "--metrics-recording-only",
            "--disable-default-apps",
            "--no-first-run",
            "--disable-setuid-sandbox",
            "--hide-scrollbars",
            "--no-sandbox",
            "--no-zygote",
            "--autoplay-policy=no-user-gesture-required",
            "--disable-notifications",
            "--disable-logging",
            "--disable-permissions-api",
            "--ignore-certificate-errors",
        ]:
            options.add_argument(arg)
        # hide infobar about automation
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.capabilities["acceptInsecureCerts"] = True
        # workaround for the first page being way to slow to load
        # ~2 minutes for my case (caused by some useless element being slow?)
        options.page_load_strategy = "eager"
        super().__init__(options=options)
        self.environment = environment
        self.start_time = None
        time.sleep(1)
        self.command_executor._commands["SEND_COMMAND"] = ("POST", "/session/$sessionId/chromium/send_command")
        # self.execute(
        #     "SEND_COMMAND",
        #     dict(
        #         cmd="Network.emulateNetworkConditions",
        #         params={"offline": False, "latency": 100, "downloadThroughput": 10000, "uploadThroughput": 10000},
        #     ),
        # )

    def find_element(self, by=By.ID, value=None, name=None, prefix="", retry=0):  # pylint: disable=arguments-differ
        element = None
        if name and prefix:
            raise Exception("dont specify both name and prefix, that makes no sense")
        if not name:
            name = f"{prefix.ljust(13)} {by[0:5]} {value}"
        if not self.start_time:
            self.start_time = time.monotonic()
        try:
            element = super().find_element(by=by, value=value)
            self.execute_script("arguments[0].scrollIntoView(true);", element)
            if not self.headless:
                time.sleep(0.1)
                # show a visual indication on the element we've found (and probably are about to interact with)
                self.execute_script("arguments[0].style.border='3px solid red'", element)
                time.sleep(2)
                self.execute_script("arguments[0].style.border='0px'", element)
                time.sleep(0.1)

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
            self.environment.events.request.fire(
                request_type="find",
                name=name,
                response_time=total_time,
                response_length=0,
                context={},
                exception=error_message,
            )
            if not isinstance(e, WebDriverException):
                raise
        else:
            total_time = (time.monotonic() - self.start_time) * 1000
            self.start_time = None
            self.environment.events.request_success.fire(
                request_type="find", name=name, response_time=total_time, response_length=0
            )
        return element


class WebdriverUser(User):

    abstract = True
    _first_instance = True

    def __init__(self, parent, headless=True):
        super().__init__(parent)
        self.headless = headless
        if WebdriverUser._first_instance:
            WebdriverUser._first_instance = False
            # kill old webdriver browser instances
            subprocess.Popen(["killall", "chromedriver"], stderr=subprocess.DEVNULL)
            subprocess.Popen(["pkill", "-f", " --test-type=webdriver"], stderr=subprocess.DEVNULL)

        self.client = WebdriverClient(self.environment, headless)
        time.sleep(1)

    def clear(self):
        for _ in range(3):
            try:
                self.client.execute("SEND_COMMAND", dict(cmd="Network.clearBrowserCache", params={}))
                # clearBrowserCookies is better than self.delete_all_cookies(), because it also clears http-only cookies
                self.client.execute("SEND_COMMAND", dict(cmd="Network.clearBrowserCookies", params={}))
                break
            except (InvalidSessionIdException, WebDriverException):
                time.sleep(1)
        else:
            self.client.quit()
            self.client = WebdriverClient(self.environment, self.headless)
            raise Exception("could not clear, spawned new client instead")

    def on_stop(self):
        self.client.close()

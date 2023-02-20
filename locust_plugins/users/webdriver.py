# See examples/webdriver_ex.py for more documentation
import subprocess
import time
from locust import User
from locust.exception import CatchResponseError, LocustError
from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    InvalidSessionIdException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import greenlet
import datetime


class WebdriverClient(webdriver.Remote):
    def __init__(self, user: User):
        self.user = user
        options = Options()
        options.headless = self.user.headless
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
        super().__init__(command_executor=self.user.command_executor, options=options)
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

    def locust_find_element(
        self, by=By.ID, value=None, name=None, prefix="", retry=0, context=None, fake_success=False
    ):  # pylint: disable=arguments-differ
        element = None
        context = context or {}
        if self.user:
            context = {**self.user.context(), **context}
        if name and prefix:
            raise Exception("dont specify both name and prefix, that makes no sense")
        if not name:
            name = f"{prefix.ljust(13)} {by[0:5]} {value}"
        if not self.start_time:
            self.start_time = time.perf_counter()
        try:
            element = super().find_element(by=by, value=value)
            # self.execute_script("arguments[0].scrollIntoView(true);", element)
            if not self.user.headless:
                time.sleep(0.1)
                # show a visual indication on the element we've found (and probably are about to interact with)
                self.execute_script("arguments[0].style.border='3px solid red'", element)
                time.sleep(2)
                self.execute_script("arguments[0].style.border='0px'", element)
                time.sleep(0.1)

        except Exception as e:
            if retry < 2:
                return self.locust_find_element(by=by, value=value, name=name, retry=retry + 1)
            total_time = (time.perf_counter() - self.start_time) * 1000
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
            identifier = context.get("ssn", greenlet_id)  # kind of SvS specific
            if not fake_success:
                self.save_screenshot(
                    f"{timestring}_{name.replace(' ', '_').replace('{','_').replace('}','_').replace(':','_')}_{identifier}.png"
                )

                self.user.environment.events.request.fire(
                    request_type="find",
                    name=name,
                    response_time=total_time,
                    response_length=0,
                    context=context,
                    exception=error_message,
                    url=self.current_url,
                )
                self.start_time = None
                if not isinstance(e, WebDriverException):
                    raise
        else:
            total_time = (time.perf_counter() - self.start_time) * 1000
            self.user.environment.events.request.fire(
                request_type="find",
                name=name,
                response_time=total_time,
                response_length=0,
                context=context,
                exception=None,
                url=self.current_url,
            )
            self.start_time = None
        return element


class WebDriverResponseContextManager:
    """
    A Response like class that also acts as a context manager that provides the ability to manually
    control if the webdriver session request should be marked as successful or a failure in Locust's statistics
    Use the two additional methods: :py:meth:`success <locust.clients.ResponseContextManager.success>` and
    :py:meth:`failure <locust.clients.ResponseContextManager.failure>` to update the locust stats.

    This class is based on Locust ResponseContextManager
    """

    _manual_result = None
    _entered = False

    def __init__(self, user, client, request_event, request_meta):
        self.client = client
        self.user = user
        self._request_event = request_event
        self.request_meta = request_meta

    def __enter__(self):
        self._entered = True
        if not self.request_meta["start_time"]:
            self.request_meta["start_time"] = time.perf_counter()

        return self

    def __exit__(self, exc, value, traceback):
        # if the user has already manually marked this response as failure or success
        # we can ignore the default behaviour of letting the response code determine the outcome
        if self._manual_result is not None:
            if self._manual_result is True:
                self.request_meta["exception"] = None
            elif isinstance(self._manual_result, Exception):
                self.request_meta["exception"] = self._manual_result
            self._report_request()
            return exc is None

        # no manual result fired - set stop time as current time
        self.request_meta["response_time"] = (time.perf_counter() - self.request_meta["start_time"]) * 1000

        if exc:
            # Override the default rendering of exceptions to avoid printing complete stack traces.
            if isinstance(value, TimeoutException):
                self.request_meta["exception"] = "Timeout waiting for Webdriver:" + value.msg
                self._report_request()
            elif isinstance(value, WebDriverException):
                self.request_meta["exception"] = "Webdriver Exception:" + value.msg
                self._report_request()
            else:
                # we want other unknown exceptions to be raised
                return False
        else:
            self._report_request()

        return True

    def _report_request(self):
        # if URL is None, update with current url
        if not self.request_meta["url"]:
            self.request_meta["url"] = self.client.current_url

        self._request_event.fire(**self.request_meta)

    def success(self):
        """
        Report the response as successful
        Example::
            with self.request(name="helpful_name") as request:
                request.client.get("https://example.com/")
                title = request.client.find_element(By.CSS_SELECTOR, "body > div > h1")
                if title.text == "Example Domain":
                    request.success()
                else:
                    request.failure("Page title didn't match")
        """
        if not self._entered:
            raise LocustError(
                "Tried to set status on a request that has not yet been made. Make sure you use a with-block, like this:\n\nwith self.client.request(..., catch_response=True) as response:\n    response.success()"
            )
        self._manual_result = True
        self.request_meta["response_time"] = (time.perf_counter() - self.request_meta["start_time"]) * 1000

    def failure(self, exc):
        """
        Report the response as a failure.
        if exc is anything other than a python exception (like a string) it will
        be wrapped inside a CatchResponseError.
        Example::
            with self.request(name="helpful_name") as request:
                request.client.get("https://example.com/")
                title = request.client.find_element(By.CSS_SELECTOR, "body > div > h1")
                if title.text != "Example Domain":
                    request.success()
                else:
                    request.failure("Page title didn't match")
        """
        if not self._entered:
            raise LocustError(
                "Tried to set status on a request that has not yet been made. Make sure you use a with-block, like this:\n\nwith self.client.request(..., catch_response=True) as response:\n    response.failure(...)"
            )
        if not isinstance(exc, Exception):
            exc = CatchResponseError(exc)
        self._manual_result = exc
        self.request_meta["response_time"] = (time.perf_counter() - self.request_meta["start_time"]) * 1000


class WebdriverUser(User):
    abstract = True
    _first_instance = True
    headless = False  # overwrite this as needed
    command_executor = "http://127.0.0.1:4444"

    def __init__(self, parent):
        super().__init__(parent)
        if WebdriverUser._first_instance:
            WebdriverUser._first_instance = False
            # kill old webdriver browser instances
            subprocess.Popen(["killall", "chromedriver"], stderr=subprocess.DEVNULL)
            subprocess.Popen(["pkill", "-f", " --test-type=webdriver"], stderr=subprocess.DEVNULL)

        self.client = WebdriverClient(self)
        time.sleep(1)

    def request(self, name, context=None) -> WebDriverResponseContextManager:
        start_time = time.perf_counter()
        total_time = (time.perf_counter() - start_time) * 1000

        context = context or {}
        if self.client.user:
            context = {**self.client.user.context(), **context}

        # store meta data that is used when reporting the request to locust's statistics
        request_meta = {
            "request_type": "Webdriver",
            "response_time": total_time,
            "response_length": 0,
            "name": name,
            "context": context,
            "exception": None,
            "start_time": start_time,
            "url": None,
        }

        return WebDriverResponseContextManager(
            user=self, client=self.client, request_event=self.environment.events.request, request_meta=request_meta
        )

    def clear(self):
        for _ in range(3):
            try:
                # pylint: disable=use-dict-literal
                self.client.execute("SEND_COMMAND", dict(cmd="Network.clearBrowserCache", params={}))
                # clearBrowserCookies is better than self.delete_all_cookies(), because it also clears http-only cookies
                self.client.execute("SEND_COMMAND", dict(cmd="Network.clearBrowserCookies", params={}))
                break
            except (InvalidSessionIdException, WebDriverException):
                time.sleep(1)
        else:
            self.client.quit()
            self.client = WebdriverClient(self)
            raise Exception("could not clear, spawned new client instead")

    def clear_cookies(self):
        for _ in range(3):
            try:
                # pylint: disable=use-dict-literal
                self.client.execute("SEND_COMMAND", dict(cmd="Network.clearBrowserCookies", params={}))
                break
            except (InvalidSessionIdException, WebDriverException):
                time.sleep(1)
        else:
            self.client.quit()
            self.client = WebdriverClient(self)
            raise Exception("could not clear, spawned new client instead")

    def on_stop(self):
        self.client.close()

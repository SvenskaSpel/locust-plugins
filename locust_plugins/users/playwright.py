import logging
import os
import sys

try:
    from playwright.async_api import async_playwright, Playwright, Browser, Page, BrowserContext
except (NotImplementedError, AttributeError) as e:
    if os.getenv("LOCUST_PLAYWRIGHT", False):
        raise Exception("Could not import playwright, even though LOCUST_PLAYWRIGHT was set :(") from e
    else:
        logging.error("Set env var LOCUST_PLAYWRIGHT=1 to make locust load trio before gevent monkey patching")
        sys.exit(1)
from contextlib import asynccontextmanager, contextmanager
import asyncio
from locust import User, events, task
from locust.runners import WorkerRunner
import gevent
import ast
import types
import time
import os
import re
from locust.exception import CatchResponseError, RescheduleTask
import playwright as pw
from locust import runners
import copy
import traceback

runners.HEARTBEAT_LIVENESS = 10

loop: asyncio.AbstractEventLoop = None

# import yappi

# yappi.set_context_backend("greenlet")
# yappi.set_clock_type("wall")
# yappi.start(builtins=True)


def sync(async_func):
    """
    Make a synchronous function from an async. When called, it will be executed once for every sub-user (as specified in multiplier)
    """

    def wrapFunc(self: User, *args, **kwargs):
        futures = []

        for sub_user in self.sub_users:
            futures.append(asyncio.run_coroutine_threadsafe(async_func(sub_user, *args, **kwargs), loop))
            gevent.sleep(2)

        while True:
            for f in futures:
                if not f.done():
                    gevent.sleep(0.1)
                    break
                else:
                    e = f.exception()
                    if e:
                        raise e
            else:
                break

    return wrapFunc


@asynccontextmanager
async def event(
    user: "PlaywrightUser",
    name="unnamed",
    request_type="event",
):
    start_time = time.time()
    start_perf_counter = time.perf_counter()
    try:
        yield
        user.environment.events.request.fire(
            request_type=request_type,
            name=name,
            start_time=start_time,
            response_time=(time.perf_counter() - start_perf_counter) * 1000,
            response_length=0,
            context={**user.context()},
            url=user.page.url if user.page else None,
            exception=None,
        )
    except Exception as e:
        try:
            error = CatchResponseError(re.sub("=======*", "", e.message).replace("\n", "").replace(" logs ", " ")[:500])
        except:
            error = e  # never mind
        if not user.error_screenshot_made:
            user.error_screenshot_made = True  # dont spam screenshots...
            if user.page:  # in ScriptUser runs we have no reference to the page so...
                await user.page.screenshot(
                    path="screenshot_" + time.strftime("%Y%m%d_%H%M%S") + ".png", full_page=False
                )
        user.environment.events.request.fire(
            request_type=request_type,
            name=name,
            start_time=start_time,
            response_time=(time.perf_counter() - start_perf_counter) * 1000,
            response_length=0,
            url=user.page.url if user.page else None,
            context={**user.context()},
            exception=error,
        )
    await asyncio.sleep(0.1)


def on_console(msg):
    if (
        msg.type == "error"
        and msg.text.find("net::ERR_FAILED") == -1
        and msg.text.find("Refused to load the image") == -1
    ):
        print("err " + msg.text + ":" + msg.location["url"])


def pw(func):
    """
    1. Converts the decorated method from async to regular using sync()
    2. Sets up a new BrowserContext if there isnt one already
    3. Runs the decorated method (for all sub-users)
    """

    @sync
    async def pwwrapFunc(user: PlaywrightUser):
        if user.browser_context:
            await user.browser_context.close()
        user.browser_context = await user.browser.new_context(ignore_https_errors=True, base_url=user.host)
        # await user.browser_context.add_init_script("() => delete window.navigator.serviceWorker")
        user.page = await user.browser_context.new_page()
        user.page.set_default_timeout(60000)

        if isinstance(user, PlaywrightScriptUser):
            name = user.script
        else:
            name = user.__class__.__name__ + "." + func.__name__
        try:
            task_start_time = time.time()
            start_perf_counter = time.perf_counter()
            await func(user, user.page)
            if user.log_tasks:
                user.environment.events.request.fire(
                    request_type="TASK",
                    name=name,
                    start_time=task_start_time,
                    response_time=(time.perf_counter() - start_perf_counter) * 1000,
                    response_length=0,
                    context={**user.context()},
                    exception=None,
                    # url=user.page.url,
                )
        except RescheduleTask:
            pass  # no need to log anything, because an individual request has already failed
        except Exception as e:
            try:
                e = CatchResponseError(
                    re.sub("=======*", "", e.message + user.page.url).replace("\n", "").replace(" logs ", " ")
                )
            except:
                pass  # never mind
            if not user.error_screenshot_made:
                user.error_screenshot_made = True  # dont spam screenshots...
                if user.page:  # in ScriptUser runs we have no reference to the page so...
                    await user.page.screenshot(
                        path="screenshot_" + time.strftime("%Y%m%d_%H%M%S") + ".png", full_page=True
                    )
            if user.log_tasks:
                user.environment.events.request.fire(
                    request_type="TASK",
                    name=name,
                    start_time=task_start_time,
                    response_time=(time.perf_counter() - start_perf_counter) * 1000,
                    response_length=0,
                    context={**user.context()},
                    exception=e,
                    url=user.page.url if user.page else None,
                )
            else:
                user.environment.events.user_error.fire(user_instance=user, exception=e, tb=e.__traceback__)
                logging.error("%s\n%s", e, traceback.format_exc())

        finally:
            await user.page.wait_for_timeout(1000)  # give outstanding interactions some time
            await user.page.close()
            await user.browser_context.close()

    return pwwrapFunc


import typing
from typing_extensions import Literal
from playwright.async_api import Position


async def click_retry(
    self: "PageWithRetry",
    # I had to copy all the arguments instead of using *args/**kwargs to get type hints
    selector: str,
    *,
    modifiers: typing.Optional[typing.List[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
    position: Position = None,  # type: ignore
    delay: float = None,
    button: Literal["left", "middle", "right"] = None,
    click_count: int = None,
    timeout: float = None,
    force: bool = None,
    no_wait_after: bool = None,
    trial: bool = None,
    strict: bool = None,
    retries: int = 2,
    **kwargs,  # just in case playwright adds some parameter in the future
):
    for attempt in range(retries + 1):
        try:
            await self.click(
                selector=selector,
                modifiers=modifiers,
                position=position,
                delay=delay,
                button=button,
                click_count=click_count,
                timeout=timeout,
                force=force,
                no_wait_after=no_wait_after,
                trial=trial,
                strict=strict,
                **kwargs,
            )
        except Exception as e:
            logging.debug(f"couldnt click, got {e}")
            if attempt == retries - 1:
                raise
            gevent.sleep(0)
        else:
            break  # success!


Page.click_retry = click_retry


class PageWithRetry(Page):  # just to make autocomplete/type hinting work
    click_retry = click_retry


class PlaywrightUser(User):
    abstract = True
    headless = None
    playwright: Playwright = None
    browser: Browser = None
    browser_type = "chromium"  # "chromium", "chrome" or "firefox"
    browser_context: BrowserContext = None
    page: PageWithRetry = None
    error_screenshot_made = False
    multiplier = 1  # how many concurrent Playwright sessions/browsers to run for each Locust User instance. Setting this to ~10 is an efficient way to reduce overhead.
    sub_users = []
    log_tasks = True  # by default, every task is logged as a request (an unhandled exceptions in the task will mark it as failed)

    def __init__(self, parent):
        super().__init__(parent)
        future = asyncio.run_coroutine_threadsafe(self._pwprep(), loop)
        while not future.done():
            gevent.sleep(0.1)
        e = future.exception()
        if e:
            logging.error(e)
            sys.exit(1)
        if self.environment.runner is None:  # debug session
            self.multiplier = 1
        self.sub_users = [copy.copy(self) for _ in range(self.multiplier)]

    async def _pwprep(self):
        if self.playwright is None:
            self.playwright = await async_playwright().start()
        if self.browser is None:
            if self.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(
                    headless=self.headless or self.headless is None and self.environment.runner is not None,
                )
            elif self.browser_type in ["chromium", "chrome"]:
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless or self.headless is None and self.environment.runner is not None,
                    channel=self.browser_type,
                    args=[
                        "--disable-gpu",
                        "--disable-setuid-sandbox",
                        "--disable-accelerated-2d-canvas",
                        "--no-zygote",
                        "--frame-throttle-fps=10",
                        # didnt seem to help much:
                        # "--single-process",
                        #
                        # "--enable-profiling",
                        # "--profiling-at-start=renderer",
                        "--no-sandbox",
                        # "--profiling-flush",
                        # maybe even made it worse?
                        # "--disable-gpu-vsync",
                        # "--disable-site-isolation-trials",
                        # "--disable-features=IsolateOrigins",
                        #
                        # maybe a little better?
                        "--disable-blink-features=AutomationControlled",
                        "--disable-blink-features",
                        "--disable-translate",
                        "--safebrowsing-disable-auto-update",
                        "--disable-sync",
                        "--hide-scrollbars",
                        "--disable-notifications",
                        "--disable-logging",
                        "--disable-permissions-api",
                        "--ignore-certificate-errors",
                        # made no difference
                        "--proxy-server='direct://'",
                        "--proxy-bypass-list=*",
                        # seems to help a little?
                        # "--blink-settings=imagesEnabled=false",
                        "--host-resolver-rules=MAP www.googletagmanager.com 127.0.0.1, MAP www.google-analytics.com 127.0.0.1, MAP *.facebook.* 127.0.0.1, MAP assets.adobedtm.com 127.0.0.1, MAP s2.adform.net 127.0.0.1",
                        "--no-first-run",
                        "--disable-audio-output",
                        "--disable-canvas-aa",
                    ],
                )
            else:
                raise Exception(f"Unknown browser type specified: {self.browser_type}")


class PlaywrightScriptUser(PlaywrightUser):
    """
    This user allows Locust to run the output from Playwright's codegen without modification
    Here's how to make one:
    playwright codegen --target python-async -o my_recording.py https://mywebsite.com
    It does some black magic (parsing the recording into an AST and removing some statements)
    so it may not work if you have made manual changes to the recording.
    """

    abstract = True
    script = None

    def __init__(self, parent):
        with open(self.script, encoding="UTF-8") as f:
            code = f.read()
        p = ast.parse(code)

        def assert_source(stmt: ast.stmt, expected_line: str):
            if sys.version_info >= (3, 8):  # get_source_segment was added in 3.8
                actual_line = ast.get_source_segment(code, stmt)
                if actual_line != expected_line:
                    logging.warning(
                        f"Source code removed from Playwright recording was unexpected. Got '{actual_line}', expected '{expected_line}'"
                    )

        for node in p.body[:]:
            if isinstance(node, ast.Expr) and node.value.func.attr == "run":
                assert_source(node, "asyncio.run(main())")
                p.body.remove(node)
            elif isinstance(node, ast.AsyncFunctionDef) and node.name == "run":
                # future optimization: reuse browser instances
                page_arg = ast.arg(arg="page")
                node.args.args.append(page_arg)
                # remove setup from recording, asserting so that the lines removed were the expected ones
                assert_source(node.body.pop(0), "browser = await playwright.chromium.launch(headless=False)")
                assert_source(node.body.pop(0), "context = await browser.new_context()")
                assert_source(node.body.pop(0), "page = await context.new_page()")
                # remove teardown
                assert_source(node.body.pop(), "await browser.close()")
                assert_source(node.body.pop(), "await context.close()")
                ast.fix_missing_locations(node)

        module = types.ModuleType("mod")
        code = compile(p, self.script, "exec")
        sys.modules["mod"] = module
        exec(code, module.__dict__)  # pylint: disable=exec-used

        import mod  # type: ignore # pylint: disable-all

        self.pwrun = mod.run  # cant name it "run", because that collides with User.run

        # multiplier in the base constructor copies the instance into sub-users so we need to do this AFTER setting self.pwrun
        super().__init__(parent)

    @task
    @pw
    async def scriptrun(self, page):  # pylint: disable-all
        await self.pwrun(self.playwright, page)


@events.test_start.add_listener
def on_start(environment, **kwargs):
    global loop
    loop = asyncio.new_event_loop()
    try:
        gevent.spawn(loop.run_forever)
    except Exception as e:
        print(f"run_forever threw an exception :( {e}")


@events.test_stop.add_listener
def on_stop(environment, **kwargs):
    loop.stop()
    # yappi.stop()
    # yappi.get_func_stats().print_all()
    time.sleep(5)


@events.quitting.add_listener
def on_locust_quit(environment, **kwargs):
    # Playwright outputs control codes that alter the terminal, so we need to reset it
    # suppress any error output in case it is not a real terminal
    os.system("reset 2>/dev/null")

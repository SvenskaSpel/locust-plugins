try:
    from playwright.async_api import async_playwright, Playwright, Browser, Page, BrowserContext
except NotImplementedError as e:
    raise Exception(
        "Could not import playwright, probably because gevent monkey patching was done before trio init. Set env var LOCUST_PLAYWRIGHT=1"
    ) from e
from contextlib import asynccontextmanager
import os
import asyncio
from locust import User, events, task
import gevent
import sys
import ast
import types
import time
import os
import re
from locust.exception import CatchResponseError
import playwright as pw
import re

loop: asyncio.AbstractEventLoop = None


def sync(async_func):
    """
    Make a synchronous function from an async
    """

    def wrapFunc(self: User):
        future = asyncio.run_coroutine_threadsafe(async_func(self), loop)
        while not future.done():
            gevent.sleep(0.1)
        e = future.exception()
        if e:
            raise e

    return wrapFunc


@asynccontextmanager
async def event(user: "PlaywrightUser", name="unnamed", request_type="event"):
    task_start_time = time.time()
    start_perf_counter = time.perf_counter()
    try:
        yield
        user.environment.events.request.fire(
            request_type=request_type,
            name=name,
            start_time=task_start_time,
            response_time=(time.perf_counter() - start_perf_counter) * 1000,
            response_length=0,
            context={**user.context()},
            exception=None,
        )
    except Exception as e:
        try:
            error = CatchResponseError(re.sub("=======*", "", e.message).replace("\n", "").replace(" logs ", " "))
        except:
            error = e  # never mind
        if not user.error_screenshot_made:
            user.error_screenshot_made = True  # dont spam screenshots...
            await user.page.screenshot(path="screenshot_" + time.strftime("%H%M%S") + ".png")
        user.environment.events.request.fire(
            request_type="TASK",
            name=name,
            start_time=task_start_time,
            response_time=(time.perf_counter() - start_perf_counter) * 1000,
            response_length=0,
            context={**user.context()},
            exception=error,
        )


def pw(func):
    """
    1. Converts the decorated function from async to regular using sync()
    2. Sets up user.playwright and optionally user.browser
    3. Fires a request event after finishing.
    """

    @sync
    async def pwwrapFunc(user: PlaywrightUser):
        if user.playwright is None:
            user.playwright = await async_playwright().start()
        if isinstance(user, PlaywrightScriptUser):
            name = user.script
        else:
            if user.browser is None:
                user.browser = await user.playwright.chromium.launch(
                    headless=user.headless or user.headless is None and user.environment.runner is not None,
                    # channel="chrome",
                    args=[
                        "--disable-gpu",
                        # "--no-sandbox",
                        # "--disable-setuid-sandbox",
                        # "--disable-accelerated-2d-canvas",
                        # "--no-first-run",
                        # "--no-zygote",
                        # "--single-process",
                    ],
                    ignore_default_args=["--disable-dev-shm-usage"],  # we have plenty of space on /dev/shm
                )
            # I wish we could call this just "context" but it would collide with User.context():
            user.browser_context = await user.browser.new_context()
            user.page = await user.browser_context.new_page()
            name = user.__class__.__name__ + "." + func.__name__
        try:
            task_start_time = time.time()
            start_perf_counter = time.perf_counter()
            await func(user)
            user.environment.events.request.fire(
                request_type="TASK",
                name=name,
                start_time=task_start_time,
                response_time=(time.perf_counter() - start_perf_counter) * 1000,
                response_length=0,
                context={**user.context()},
                exception=None,
            )
        except Exception as e:
            try:
                error = CatchResponseError(re.sub("=======*", "", e.message).replace("\n", "").replace(" logs ", " "))
            except:
                error = e  # never mind
            if not user.error_screenshot_made:
                user.error_screenshot_made = True  # dont spam screenshots...
                await user.page.screenshot(path="screenshot_" + time.strftime("%H%M%S") + ".png")
            user.environment.events.request.fire(
                request_type="TASK",
                name=name,
                start_time=task_start_time,
                response_time=(time.perf_counter() - start_perf_counter) * 1000,
                response_length=0,
                context={**user.context()},
                exception=error,
            )
        finally:
            if not isinstance(user, PlaywrightScriptUser):
                await user.page.close()
                await user.browser_context.close()

    return pwwrapFunc


class PlaywrightUser(User):
    abstract = True
    headless = None
    playwright: Playwright = None
    browser: Browser = None
    browser_context: BrowserContext = None
    page: Page = None
    error_screenshot_made = False


class PlaywrightScriptUser(PlaywrightUser):
    abstract = True
    script = None

    def __init__(self, parent):
        super().__init__(parent)

        with open(self.script, encoding="UTF-8") as f:
            p = ast.parse(f.read())

        for node in p.body[:]:
            if isinstance(node, ast.Expr) and node.value.func.attr == "run":
                p.body.remove(node)  # remove "asyncio.run(main())"
            elif isinstance(node, ast.AsyncFunctionDef) and node.name == "run":
                # future optimization: reuse browser instances
                launch_line = node.body[0]  # browser = await playwright.chromium.launch(headless=False)
                # default is for full Locust runs to be headless, but for debug runs to show the browser
                if self.headless or self.headless is None and self.environment.runner is not None:
                    launch_line.value.value.keywords[0].value.value = True  # overwrite headless parameter

        module = types.ModuleType("mod")
        code = compile(p, self.script, "exec")
        sys.modules["mod"] = module
        exec(code, module.__dict__)  # pylint: disable=exec-used

        import mod  # type: ignore # pylint: disable-all

        PlaywrightUser.pwrun = mod.run  # cant name it "run", because that collides with User.run

    @task
    @pw
    async def scriptrun(self):  # pylint: disable-all
        await PlaywrightUser.pwrun(self.playwright)


@events.test_start.add_listener
def on_start(**_kwargs):
    global loop
    loop = asyncio.new_event_loop()
    try:
        gevent.spawn(loop.run_forever)
    except Exception as e:
        print(f"run_forever threw an exception :( {e}")


@events.test_stop.add_listener
def on_stop(**_kwargs):
    loop.stop()
    time.sleep(5)


@events.quitting.add_listener
def on_locust_quit(environment, **_kwargs):
    # Playwright outputs control codes that alter the terminal, so we need to reset it
    # suppress any error output in case it is not a real terminal
    os.system("reset 2>/dev/null")

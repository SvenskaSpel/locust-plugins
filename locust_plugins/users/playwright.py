try:
    from playwright.async_api import async_playwright
except NotImplementedError as e:
    raise Exception(
        "Could not import playwright, probably because gevent monkey patching was done before trio init. Set env var LOCUST_PLAYWRIGHT=1"
    ) from e
import asyncio
from locust import TaskSet, User, events, task
from locust.user.task import DefaultTaskSet
import locust
import gevent
import sys
import ast
import types
import time
import os
import contextvars
import re
from locust.exception import CatchResponseError
from inspect import iscoroutinefunction
import playwright as pw

loop: asyncio.AbstractEventLoop = None


def time_task(func):
    async def wrapFunc(user):
        try:
            test_start_time = time.time()
            await func(user)
            user.environment.events.request.fire(
                request_type="TASK",
                name=user.__class__.__name__,
                start_time=test_start_time,
                response_time=(time.time() - test_start_time) * 1000,
                response_length=0,
                context={},
                exception=None,
            )
        except Exception as e:
            message = re.sub("=======*", "", e.message).replace("\n", "").replace(" logs ", " ")
            user.environment.events.request.fire(
                request_type="TASK",
                name=user.__class__.__name__,
                start_time=test_start_time,
                response_time=(time.time() - test_start_time) * 1000,
                response_length=0,
                context={},
                exception=CatchResponseError(message),
            )

    return wrapFunc


def run_coro(coro, sleep=1):
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    while not future.done():
        gevent.sleep(sleep)
    e = future.exception()
    if e:
        raise e


async def set_playwright(self: User, launch_browser: bool):
    self.playwright = await async_playwright().start()
    if launch_browser:
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless or self.headless is None and self.environment.runner is not None
        )


def execute_task(self, task):
    user = self.user
    if hasattr(task, "tasks") and issubclass(task, TaskSet):
        # task is  (nested) TaskSet class
        task(user).run()
    else:  # task is a function
        if iscoroutinefunction(task):
            if user.playwright is None:
                run_coro(set_playwright(user, task.__name__ != "scriptrun"))
            run_coro(task(user))
        else:
            task(user)


DefaultTaskSet.execute_task = execute_task


class PlaywrightUser(User):
    abstract = True
    headless = None
    browser = None
    playwright = None


class PlaywrightScriptUser(PlaywrightUser):
    abstract = True

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
    @time_task
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

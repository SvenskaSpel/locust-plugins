try:
    from playwright.async_api import async_playwright
except NotImplementedError as e:
    raise Exception(
        "Could not import playwright, probably because gevent monkey patching was done before trio init. Set env var LOCUST_PLAYWRIGHT=1"
    ) from e
import asyncio
from locust import User, events
import locust
import gevent
import sys
import ast
import types
import time
import os
import contextvars

loop: asyncio.AbstractEventLoop = None


class PlaywrightUser(User):
    abstract = True
    headless = None
    script = None
    user_contextvar = contextvars.ContextVar("user")

    def __init__(self, parent):
        super().__init__(parent)

        if self.script:
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

    async def task(self, playwright):  # pylint: disable-all
        raise Exception("override this or specify a script!")

    async def f(self):
        try:
            playwright = await async_playwright().start()
            scenario_start_time = time.time()
            if self.script:
                await self.__class__.pwrun(playwright)
            else:
                await self.task(playwright)
            self.environment.events.request.fire(
                request_type="TASK",
                name=self.__class__.__name__,
                start_time=scenario_start_time,
                response_time=(time.time() - scenario_start_time) * 1000,
                response_length=0,
                context={},
                exception=None,
            )
        except Exception as e:
            print(e)
            self.environment.events.request.fire(
                request_type="TASK",
                name=self.__class__.__name__,
                start_time=scenario_start_time,
                response_time=(time.time() - scenario_start_time) * 1000,
                response_length=0,
                context={},
                exception=e,
            )

    @locust.task
    def run_f(self):
        future = asyncio.run_coroutine_threadsafe(self.f(), loop)
        while not future.done():
            gevent.sleep(1)
        e = future.exception()
        if e:
            raise e


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

import asyncio
from playwright.async_api import async_playwright
from locust import User, task
import gevent
import sys
import ast
import types
import time


class PlaywrightUser(User):
    abstract = True
    headless = None
    script = None
    loop = asyncio.new_event_loop()
    loop_run_forever_greenlet = None

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
                    # node.body.pop()  # remove "browser = await playwright.chromium.launch(headless=False)"

                    # default is for full Locust runs to be headless, but for debug runs to show the browser
                    if self.headless or self.headless is None and self.environment.runner is not None:
                        node.body[0].value.value.keywords[0].value.value = True  # overwrite headless parameter

            module = types.ModuleType("mod")
            code = compile(p, self.script, "exec")
            sys.modules["mod"] = module
            exec(code, module.__dict__)  # pylint: disable=exec-used

            import mod  # type: ignore # pylint: disable-all

            PlaywrightUser.pwrun = mod.run  # cant name it "run", because that collides with User.run

    # these things should be moved to test_start/stop
    def on_start(self):
        if not PlaywrightUser.loop_run_forever_greenlet:
            PlaywrightUser.loop_run_forever_greenlet = True  # just in case another on_start is called semi-concurrently
            PlaywrightUser.loop_run_forever_greenlet = gevent.spawn(PlaywrightUser.loop.run_forever)

    def on_stop(self):
        if PlaywrightUser.loop_run_forever_greenlet:
            PlaywrightUser.loop_run_forever_greenlet = None
            PlaywrightUser.loop.stop()

    async def f(self):
        scenario_start_time = time.time()
        try:
            playwright = await async_playwright().start()
            await self.__class__.pwrun(playwright)
            self.environment.events.request.fire(
                request_type="flow",
                name="triss",
                start_time=scenario_start_time,
                response_time=(time.time() - scenario_start_time) * 1000,
                response_length=0,
                context={},
                exception=None,
            )
        except Exception as e:
            print(e)
            self.environment.events.request.fire(
                request_type="flow",
                name="triss",
                start_time=scenario_start_time,
                response_time=(time.time() - scenario_start_time) * 1000,
                response_length=0,
                context={},
                exception=e,
            )

    @task
    def t(self):
        future = asyncio.run_coroutine_threadsafe(self.f(), PlaywrightUser.loop)
        while not future.done():
            gevent.sleep(1)
        if e := future.exception():
            raise e

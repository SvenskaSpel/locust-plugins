from gevent import monkey
import os
import sys
from locust.env import Environment
from locust_plugins import listeners
import locust.log
from locust import User, argument_parser


def _gevent_debugger_patch():
    """This is a workaround for gevent hanging during monkey patching when a debugger is attached
    Original code by ayzerar at https://github.com/Microsoft/PTVS/issues/2390"""

    if not os.getenv("VSCODE_PID") and not os.getenv("TERM_PROGRAM") == "vscode":
        # Dont patch if VS is not running (because then there probably is no debugger and
        # we would just hang, waiting for it)
        return

    monkey.patch_all()
    saved_modules = {}
    try:
        green_modules = set(
            [
                "socket",
                "ssl",
                "select",
                "urllib",
                "thread",
                "threading",
                "time",
                "logging",
                "os",
                "signal",
                "subprocess",
                "requests",
            ]
        )
        for modname in list(sys.modules.keys()):
            if modname.partition(".")[0] in green_modules:
                saved_modules[modname] = sys.modules.pop(modname)
    finally:
        sys.modules.update(saved_modules)


def run_single_user(
    locust_class: User,
    env=None,
    catch_exceptions=False,
    include_length=False,
    include_time=False,
    include_context=False,
    init_listener=None,
    loglevel=None,
):
    _gevent_debugger_patch()
    if loglevel:
        locust.log.setup_logging(loglevel)
    if env is None:
        env = Environment()
        env.parsed_options = argument_parser.parse_options()
        listeners.Print(env, include_length=include_length, include_time=include_time, include_context=include_context)
    env.events.init.fire(environment=env, runner=None, web_ui=None)
    if init_listener:
        init_listener(env)
    locust_class._catch_exceptions = catch_exceptions
    locust_class(env).run()

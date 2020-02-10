import os
from gevent import monkey
import sys
import json


def gevent_debugger_patch(host="0.0.0.0", port=5678):
    """This is a workaround for gevent hanging during monkey patching when a debugger is attached

    Make sure to call this function before importing locust/anything else that relies on gevent!

    Original code by ayzerar at https://github.com/Microsoft/PTVS/issues/2390"""

    if sys.argv[0].endswith("locust") or (not os.getenv("VSCODE_PID") and not os.getenv("TERM_PROGRAM") == "vscode"):
        # Dont patch if we're running the full locust runtime (because it hangs in patching) or
        # if vs is not running (because then there probably is no debugger and
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


def print_json_on_decode_fail():
    old_init = json.JSONDecodeError.__init__

    def new_init(self, *k, **kw):
        old_init(self, *k, **kw)
        print(f'json was: "{k[1]}"')

    json.JSONDecodeError.__init__ = new_init

from gevent import monkey
import sys


def setup_ptvsd(host="0.0.0.0", port=5678):
    """This is a workaround for gevent hanging during monkey patching when a debugger is attached

    Make sure to call setup_ptvsd() before importing locust/anything else that relies on gevent

    Original code by ayzerar at https://github.com/Microsoft/PTVS/issues/2390"""

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

        import ptvsd  # pylint: disable=W0611

        ptvsd.enable_attach(address=(host, port), redirect_output=False)
    finally:
        sys.modules.update(saved_modules)

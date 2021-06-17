# Example of how to use VS Code debugger with Locust.
# Make sure you set "gevent": true in your launch.json

# In recent versions of VSCode you might get the following warning. I dont know why, but it seems safe to ignore.
#
# PYDEV DEBUGGER WARNING:
# sys.settrace() should not be used when the debugger is being used.
# This may cause the debugger to stop working correctly.
# If this is needed, please check:
# http://pydev.blogspot.com/2007/06/why-cant-pydev-debugger-work-with.html
# to see how to restore the debug tracing back correctly.
#
# (if you know why this happens, please let me know :)

from locust import task, HttpUser
from locust.exception import StopUser
from locust_plugins import run_single_user


class MyUser(HttpUser):
    @task
    def t(self):
        self.client.get("/", context={"foo": 1})
        self.client.get("/", context={"bar": 2})
        raise StopUser()


# when executed as a script, run a single locust in a way suitable for the vs code debugger
if __name__ == "__main__":
    MyUser.host = "http://example.edu"
    run_single_user(MyUser, include_length=True, include_time=True, include_context=True)
    # You should get output similar to this:
    #
    # time                            type    name                                                    resp_ms length  exception       context
    # 2021-06-18 01:37:23.029486      GET     /                                                       358     1256                    {'foo': 1}
    # 2021-06-18 01:37:23.188831      GET     /                                                       159     1256                    {'bar': 2}

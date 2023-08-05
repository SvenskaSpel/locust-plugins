from locust.exception import (
    RescheduleTask,
    StopUser,
    InterruptTaskSet,
)
import locust.env
import gevent
import sys
from typing import Callable


class RescheduleTaskOnFail:
    """make sure to add this listener LAST, because any failures will throw an exception,
    causing other listeners to be skipped"""

    def __init__(self, env: locust.env.Environment):
        env.events.request.add_listener(self.request)

    def request(self, exception, **kwargs):
        if exception:
            raise RescheduleTask(exception)


class InterruptTaskOnFail:
    """make sure to add this listener LAST, because any failures will throw an exception,
    causing other listeners to be skipped"""

    def __init__(self, env: locust.env.Environment):
        env.events.request.add_listener(self.request)

    def request(self, exception, **kwargs):
        if exception:
            raise InterruptTaskSet()


class StopUserOnFail:
    """make sure to add this listener LAST, because any failures will throw an exception,
    causing other listeners to be skipped"""

    def __init__(self, env: locust.env.Environment):
        env.events.request.add_listener(self.request)

    def request(self, exception, **kwargs):
        if exception:
            raise StopUser()


class ExitOnFail:
    """make sure to add this listener LAST, because any failures will throw an exception,
    causing other listeners to be skipped"""

    def __init__(self, env: locust.env.Environment):
        env.events.request.add_listener(self.request)

    def request(self, exception, **kwargs):
        if exception:
            gevent.sleep(0.2)  # wait for other listeners output to flush / write to db
            sys.exit(1)


class QuitOnFail:
    """make sure to add this listener LAST, because any failures will throw an exception,
    causing other listeners to be skipped"""

    def __init__(self, env: locust.env.Environment, name=None):
        self.name = name
        self.env = env
        env.events.request.add_listener(self.request)

    def request(self, exception, name, **kwargs):
        if exception and (name == self.name or not self.name):
            gevent.sleep(0.2)  # wait for other listeners output to flush / write to db
            self.env.runner.quit()


class RunOnFail:
    def __init__(self, env: locust.env.Environment, function: Callable):
        # execute the provided function on failure
        self.function = function
        env.events.request.add_listener(self.request)

    def request(self, exception, **kwargs):
        if exception:
            self.function(exception, **kwargs)


class RunOnUserError:
    def __init__(self, env: locust.env.Environment, function: Callable):
        # execute the provided function on unhandled exception in a task
        self.function = function
        env.events.user_error.add_listener(self.user_error)

    def user_error(self, user_instance, exception, tb, **kwargs):
        if exception:
            self.function(user_instance, exception, tb, **kwargs)

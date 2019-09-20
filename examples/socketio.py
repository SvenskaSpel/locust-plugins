#!/usr/bin/env python3
import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()

from locust import task
from locust.core import TaskSet
from locust_plugins.locusts import SocketIOLocust  # pylint: disable=ungrouped-imports
import locust_plugins.listeners  # pylint: disable=ungrouped-imports


class UserBehaviour(TaskSet):
    @task
    def my_task(self):
        # example of subscribe
        self.locust.send('42["subscribe",{"url":"/sport/matches/11995208/draws","sendInitialUpdate": true}]')
        # you can do http in the same taskset as well
        self.client.get("/")
        # wait for pushes, while occasionally sending heartbeats, like a real client would
        self.locust.sleep_with_heartbeat(10)


class MySocketIOLocust(SocketIOLocust):
    task_set = UserBehaviour
    min_wait = 0
    max_wait = 0
    if __name__ == "__main__":
        host = "http://example.com"


# allow running as executable for debugging
if __name__ == "__main__":
    locust_plugins.listeners.PrintListener()
    MySocketIOLocust().run()

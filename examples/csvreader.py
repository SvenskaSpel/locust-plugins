import locust_plugins.utils

locust_plugins.utils.gevent_debugger_patch()
from locust_plugins.readers import CSVReader
from locust_plugins.listeners import PrintListener
from locust import HttpLocust, TaskSet, task

ssn_reader = CSVReader("ssn.csv")


class MyTaskSet(TaskSet):
    @task
    def index(self):
        customer = next(ssn_reader)
        self.client.get(f"/?ssn={customer[0]}")


class MyHttpLocust(HttpLocust):
    task_set = MyTaskSet
    min_wait = 100
    max_wait = 100
    host = "http://example.com"


# allow running as executable, mainly to support attaching the debugger
if __name__ == "__main__":
    PrintListener()
    MyHttpLocust().run()

from locust import HttpUser, FastHttpUser, task
from locust_plugins.connection_pools import FastHttpPool, RequestPool


class RequestPoolExample(HttpUser):
    """HttpUser using requestPool"""

    def on_start(self):
        self.pool = RequestPool(user=self)

        # Alternatively, you can override the client attribute of the user
        # but if you have any type checking tools setup they will complain
        # self.client = RequestPool(user=self) # type: ignore

    @task
    def task_1(self):
        """example task"""
        self.pool.get(url="/")
        # self.client.get(url="/foo/bar")

    @task
    def task_2(self):
        """example task"""
        payload = {"bin": "baz"}
        self.pool.post(url="/foo/bar", data=payload)
        # self.client.get(url="/foo/bar", data=payload)


class FastHttpPoolExample(FastHttpUser):
    """FastHttpUser using"""

    def on_start(self):
        self.pool = FastHttpPool(user=self)
        # self.client = FastHttpPool(user=self) # type: ignore

    @task
    def task_1(self):
        """example task"""
        self.pool.get(path="/")
        # self.client.get(url="/foo/bar")

    @task
    def task_2(self):
        """example task"""
        payload = {"bin": "baz"}
        self.pool.post(path="/foo/bar", data=payload)
        # self.client.get(url="/foo/bar", data=payload)

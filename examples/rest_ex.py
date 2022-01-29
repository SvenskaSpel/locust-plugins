"""
RestUser is a convenience class for testing RESTful JSON endpoints.
It extends FastHttpUser by adding the `rest`-method, a wrapper around self.client.request() that:
* automatically passes catch_response=True
* automatically sets content-type and accept headers to application/json (unless you have provided your own headers)
* automatically checks that the response is valid json, parses it into a RestResponse and saves it in a field called `js` in the response object.
    (RestResponse support safe navication so if your json was {"foo": 42}, resp.js["bar"]["baz"] returns None instead of throwing an exception)
* catches any exceptions thrown in your with-block and fails the sample (this probably should have been the default behaviour in Locust)
"""

from contextlib import contextmanager
from locust import task, run_single_user
from locust.contrib.fasthttp import ResponseContextManager
from locust.user.wait_time import constant
import locust_plugins
from locust_plugins.users import RestUser


class MyUser(RestUser):
    host = "https://postman-echo.com"
    wait_time = constant(180)  # be nice to postman-echo.com, and dont run this at scale.

    @task
    def t(self):
        # should work
        with self.rest("GET", "/get", json={"foo": 1}) as resp:
            if resp.js["args"]["foo"] != 1:
                resp.failure(f"Unexpected value of foo in response {resp.text}")

        # should work
        with self.rest("POST", "/post", json={"foo": 1}) as resp:
            if resp.js["data"]["foo"] != 1:
                resp.failure(f"Unexpected value of foo in response {resp.text}")

        # RestResponse support safe navigation returning None if fields are missing (instead of throwing KeyError or
        with self.rest("POST", "/post", json={"foo": 1}) as resp:
            if resp.js["field that doesnt exist"]["status"] != "success":
                resp.failure(f"Bad or missing status in {resp.text}")

        # RestUser catches any most exceptions, so any programming mistakes you make automatically marks the request as a failure
        with self.rest("POST", "/post", json={"foo": 1}) as resp:
            if True == True:  # this is just to make vscode think we progress after this, because we will...
                raise Exception("oh no")

        # response isnt even json, but RestUser will already have been marked it as a failure, so we dont have to do it again
        with self.rest("GET", "/", json={"foo": 1}) as _resp:
            pass

        # 404
        with self.rest("GET", "http://example.com/", json={"foo": 1}) as _resp:
            pass

        # connection closed
        with self.rest("GET", "http://example.com:42/", json={"foo": 1}) as _resp:
            pass


class RestUserThatLooksAtErrors(RestUser):
    abstract = True

    @contextmanager
    def rest(self, method, url, **kwargs) -> ResponseContextManager:
        extra_headers = {"my_header": "my_value"}
        with super().rest(method, url, headers=extra_headers, **kwargs) as resp:
            resp: ResponseContextManager
            if resp.js and "error" in resp.js and resp.js["error"] is not None:
                resp.failure(resp.js["error"])
            yield resp


class MyOtherRestUser(RestUserThatLooksAtErrors):
    host = "https://postman-echo.com"
    wait_time = constant(180)  # be nice to postman-echo.com, and dont run this at scale.

    @task
    def t(self):
        with self.rest("GET", "/") as _resp:
            pass


if __name__ == "__main__":
    locust_plugins.run_single_user(MyUser)

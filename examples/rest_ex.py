"""
A convenience class for testing RESTful JSON endpoints.
RestUser extends FastHttpUser by adding the `rest`-method, a wrapper around self.client.request() that:
* automatically passes catch_response=True
* automatically sets content-type and accept headers to application/json (unless you have provided your own headers)
* automatically checks that the response is valid json, parses it into a dict and saves it in a field called `js` in the response object
* catches any exceptions thrown in your with-block and fails the sample (this probably should have been the default behaviour in Locust)
"""

from contextlib import contextmanager
from locust import task
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

        # will cause an exception, but RestUser catches it and simply marks the request as a failure
        with self.rest("POST", "/post", json={"foo": 1}) as resp:
            if resp.js["a field that doesnt exist"]:
                pass

        # response isnt even json, but RestUser will already have been marked it as a failure, so we dont have to do it again
        with self.rest("GET", "/", json={"foo": 1}) as resp:
            pass

        # 404
        with self.rest("GET", "http://example.com/", json={"foo": 1}) as resp:
            pass

        # connection closed
        with self.rest("GET", "http://example.com:42/", json={"foo": 1}) as resp:
            pass

class RestUserThatLooksAtErrors(RestUser):
    abstract = True
    @contextmanager

    def rest(self, method, url, headers, **kwargs) -> ResponseContextManager:
        extra_headers = {"my_header": "my_value"}
        with super().rest(method, url, headers={**headers, **extra_headers}, **kwargs) as resp:
            # 
            if "error" in resp.js and resp.js["error"] is not None:
                resp.failure(resp.js["error"])
            yield resp

class MyOtherRestUser(RestUserThatLooksAtErrors):
    @task
    def t(self):
        with self.rest("GET", "/") as resp:
            pass


if __name__ == "__main__":
    locust_plugins.run_single_user(MyUser)

from locust import FastHttpUser
from locust.clients import ResponseContextManager


class RestResponseContextManager(ResponseContextManager):
    js: dict  # This is technically an Optional, but I dont want to force everyone to check it
    error: object


class RestUser(FastHttpUser):
    """
    A convenience class for testing RESTful JSON endpoints.
    It extends FastHttpUser by adding the `rest`-method, a wrapper around self.client.request() that:
    * automatically passes catch_response=True
    * automatically sets content-type and accept headers to application/json (unless you have provided your own headers)
    * automatically checks that the response is valid json, parses it into an dict and saves it in a field called `js` in the response object.
    * catches any exceptions thrown in your with-block and fails the sample (this probably should have been the default behaviour in Locust)
    """

    abstract = True

    def __init__(self, parent):
        super().__init__(parent)  # keep pylint happy
        raise Exception(
            "RestUser has been removed. Its functionality is now part of locust.FastHttpUser, so it is no longer needed!"
        )

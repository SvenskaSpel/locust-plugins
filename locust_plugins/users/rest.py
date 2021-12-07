from contextlib import contextmanager
from locust.contrib.fasthttp import FastHttpUser
from locust.clients import ResponseContextManager
import traceback
import re
from json.decoder import JSONDecodeError


class RestUser(FastHttpUser):
    """
    A convenience class for testing RESTful JSON endpoints.
    It extends FastHttpUser by adding the `rest`-method, a wrapper around self.client.request() that:
    * automatically passes catch_response=True
    * automatically sets content-type and accept headers to application/json (unless you have provided your own headers)
    * automatically checks that the response is valid json, parses it into a dict and saves it in a field called `js` in the response object
    * catches any exceptions thrown in your with-block and fails the sample (this probably should have been the default behaviour in Locust)
    """

    abstract = True
    _callstack_regex = re.compile(r'  File "(\/.[^"]*)", line (\d*),(.*)')

    @contextmanager
    def rest(self, method, url, **kwargs) -> ResponseContextManager:
        headers = kwargs.pop("headers", {"Content-Type": "application/json", "Accept": "application/json"})
        with self.client.request(method, url, catch_response=True, headers=headers, **kwargs) as resp:
            resp: ResponseContextManager
            resp.js = None
            if resp.text is None:
                # round the response time to nearest second to improve error grouping
                response_time = round(resp.request_meta["response_time"] / 1000, 1)
                resp.failure(
                    f"response body None, error {resp.error}, response code {resp.status_code}, response time ~{response_time}s"
                )
            else:
                if resp.text:
                    try:
                        resp.js = resp.json()
                    except JSONDecodeError as e:
                        resp.failure(
                            f"Could not parse response as JSON. {resp.text[:250]}, response code {resp.status_code}, error {e}"
                        )
            try:
                yield resp
            except Exception as e:
                error_lines = []
                for l in traceback.format_exc().split("\n"):
                    m = self._callstack_regex.match(l)
                    if m:
                        filename = re.sub(r"/(home|Users/\w*)/", "~/", m.group(1))
                        error_lines.append(filename + ":" + m.group(2) + m.group(3))
                    short_resp = resp.text[:200] if resp.text else resp.text
                    resp.failure(f"{e.__class__.__name__}: {e} at {', '.join(error_lines)}. Response was {short_resp}")

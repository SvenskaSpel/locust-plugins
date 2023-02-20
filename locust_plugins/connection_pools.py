"""
Connection pools can be used to pad out the number of ports occupied by each user.
This is potentially useful in low user count high throughput scenarios, where the
target load balancer may not behaving as expected.

Follow up information on Azure:
https://docs.microsoft.com/en-us/azure/load-balancer/distribution-mode-concepts
Follow up information on AWS:
https://docs.aws.amazon.com/AmazonECS/latest/developerguide/load-balancer-types.html
"""

from contextlib import contextmanager
from typing import List, Optional, Generator
from locust import FastHttpUser, HttpUser, events
from locust.clients import HttpSession
from locust.contrib.fasthttp import FastHttpSession
from itertools import cycle
from argparse import ArgumentParser


@events.init_command_line_parser.add_listener
def _(parser: ArgumentParser):
    parser.add_argument(
        "--pool_size",
        type=int,
        env_var="POOL_SIZE",
        default=20,
        help="inflate the number of connections that a user uses",
    )


class FastHttpPool:
    def __init__(self, *, user: FastHttpUser, size: Optional[int] = None):
        """
        Connection pool for the FastHttpUser, the user will use the connections
        in round robin style for every HTTP request.

        Args:
            user (FastHttpUser): Instance of a FastHttpUSer, pass in self in most circumstances
            size (int, optional): [description]. Override for the pool size, value defaults to
            the input from the command line.
        """
        if size:
            self.size = size
        else:
            self.size = user.environment.parsed_options.pool_size  # type: ignore

        self._pool: List[FastHttpSession] = []
        self.request_name = None

        for _ in range(self.size):
            self._pool.append(
                FastHttpSession(
                    environment=user.environment,
                    base_url=user.host,
                    network_timeout=user.network_timeout,
                    connection_timeout=user.connection_timeout,
                    max_redirects=user.max_redirects,
                    max_retries=user.max_retries,
                    insecure=user.insecure,
                    concurrency=user.concurrency,
                    user=user,
                )
            )

        self.pool = cycle(self._pool)

    @contextmanager
    def rename_request(self, name: str) -> Generator[None, None, None]:
        """Group requests using the "with" keyword"""

        self.request_name = name
        try:
            yield
        finally:
            self.request_name = None

    def delete(self, path, name=None, **kwargs):
        """sends a DELETE request"""

        # account for the situation that name can be passed in as a keyword arg
        request_name = name if name else self.request_name

        return next(self.pool).delete(path, name=request_name, **kwargs)

    def get(self, path, name=None, **kwargs):
        """Sends a GET request"""

        request_name = name if name else self.request_name

        return next(self.pool).get(path, name=request_name, **kwargs)

    def head(self, path, name=None, **kwargs):
        """Sends a HEAD request"""

        request_name = name if name else self.request_name

        return next(self.pool).head(path, name=request_name, **kwargs)

    def options(self, path, name=None, **kwargs):
        """Sends a OPTIONS request"""

        request_name = name if name else self.request_name

        return next(self.pool).options(path, name=request_name, **kwargs)

    def patch(self, path, data=None, name=None, **kwargs):
        """Sends a PATCH request"""

        request_name = name if name else self.request_name

        return next(self.pool).patch(path, data=data, name=request_name, **kwargs)

    def post(self, path, data=None, name=None, **kwargs):
        """Sends a POST request"""

        request_name = name if name else self.request_name

        return next(self.pool).post(path, data=data, name=request_name, **kwargs)

    def put(self, path, data=None, name=None, **kwargs):
        """Sends a PUT request"""

        request_name = name if name else self.request_name

        return next(self.pool).put(path, data=data, name=request_name, **kwargs)


class RequestPool:
    def __init__(self, *, user: HttpUser, size: Optional[int] = None):
        """
        Connection pool for the HttpUser, the user will use the connections
        in round robin style for every HTTP request.

        Args:
            user (HttpUser): Instance of a HttpUser, pass in self in most circumstances
            size (int, optional): [description]. Override for the pool size, value defaults to
            the input from the command line.
        """
        if size:
            self.size = size
        else:
            self.size = user.environment.parsed_options.pool_size  # type: ignore

        self._pool: List[HttpSession] = []
        self.request_name = None

        for _ in range(self.size):
            self._pool.append(
                HttpSession(
                    base_url=user.host, request_event=user.environment.events.request, user=user  # type: ignore
                )
            )

        self.pool = cycle(self._pool)

    @contextmanager
    def rename_request(self, name: str) -> Generator[None, None, None]:
        """Group requests using the "with" keyword"""

        self.request_name = name
        try:
            yield
        finally:
            self.request_name = None

    def delete(self, url, name=None, **kwargs):
        """sends a DELETE request"""

        # account for the situation that name can be passed in as a keyword arg
        request_name = name if name else self.request_name

        return next(self.pool).delete(url=url, name=request_name, **kwargs)

    def get(self, url, name=None, **kwargs):
        """Sends a GET request"""

        request_name = name if name else self.request_name

        return next(self.pool).get(url=url, name=request_name, **kwargs)

    def head(self, url, name=None, **kwargs):
        """Sends a HEAD request"""

        request_name = name if name else self.request_name

        return next(self.pool).head(url=url, name=request_name, **kwargs)

    def options(self, url, name=None, **kwargs):
        """Sends a OPTIONS request"""

        request_name = name if name else self.request_name

        return next(self.pool).options(url=url, name=request_name, **kwargs)

    def patch(self, url, data=None, name=None, **kwargs):
        """Sends a PATCH request"""

        request_name = name if name else self.request_name

        return next(self.pool).patch(url=url, data=data, name=request_name, **kwargs)

    def post(self, url, data=None, name=None, **kwargs):
        """Sends a POST request"""

        request_name = name if name else self.request_name

        return next(self.pool).post(url=url, data=data, name=request_name, **kwargs)

    def put(self, url, data=None, name=None, **kwargs):
        """Sends a PUT request"""

        request_name = name if name else self.request_name

        return next(self.pool).put(url=url, data=data, name=request_name, **kwargs)


class ForceNewFastHTTPObj:
    def __init__(self, *, user: FastHttpUser):
        """A class that deals with Load balancer stickyness in a more agressive way.
        For a every request a new session will be created and destroyed.
        May negatively impact local performance

        Args:
        user (HttpUser): Instance of a HttpUser, pass in self in most circumstances
        """

        self.request_name = None
        self.session_info = {
            "environment": user.environment,
            "base_url": user.host,
            "network_timeout": user.network_timeout,
            "connection_timeout": user.connection_timeout,
            "max_redirects": user.max_redirects,
            "max_retries": user.max_retries,
            "insecure": user.insecure,
            "concurrency": user.concurrency,
            "user": user,
        }

    @contextmanager
    def rename_request(self, name: str) -> Generator[None, None, None]:
        """Group requests using the "with" keyword"""

        self.request_name = name
        try:
            yield
        finally:
            self.request_name = None

    def delete(self, path, name=None, **kwargs):
        """sends a DELETE request"""

        request_name = name if name else self.request_name

        return FastHttpSession(**self.session_info).delete(path=path, name=request_name, **kwargs)

    def get(self, path, name=None, **kwargs):
        """Sends a GET request"""

        request_name = name if name else self.request_name

        return FastHttpSession(**self.session_info).get(path=path, name=request_name, **kwargs)

    def head(self, path, name=None, **kwargs):
        """Sends a HEAD request"""

        request_name = name if name else self.request_name

        return FastHttpSession(**self.session_info).head(path=path, name=request_name, **kwargs)

    def options(self, path, name=None, **kwargs):
        """Sends a OPTIONS request"""

        request_name = name if name else self.request_name

        return FastHttpSession(**self.session_info).options(path=path, name=request_name, **kwargs)

    def patch(self, path, data=None, name=None, **kwargs):
        """Sends a PATCH request"""

        request_name = name if name else self.request_name

        return FastHttpSession(**self.session_info).patch(path=path, data=data, name=request_name, **kwargs)

    def post(self, path, data=None, name=None, **kwargs):
        """Sends a POST request"""

        request_name = name if name else self.request_name

        return FastHttpSession(**self.session_info).post(path=path, data=data, name=request_name, **kwargs)

    def put(self, path, data=None, name=None, **kwargs):
        """Sends a PUT request"""

        request_name = name if name else self.request_name

        return FastHttpSession(**self.session_info).put(path=path, data=data, name=request_name, **kwargs)


class ForceNewRequestObj:
    def __init__(self, *, user: HttpUser):
        """A class that deals with Load balancer stickyness in a more agressive way.
        For a every request a new session will be created and destroyed.
        May negatively impact local performance

        Args:
        user (HttpUser): Instance of a HttpUser, pass in self in most circumstances
        """

        self.request_name = None
        self.session_info = {"base_url": user.host, "request_event": user.environment.events.request, "user": user}

    @contextmanager
    def rename_request(self, name: str) -> Generator[None, None, None]:
        """Group requests using the "with" keyword"""

        self.request_name = name
        try:
            yield
        finally:
            self.request_name = None

    def delete(self, url, name=None, **kwargs):
        """sends a DELETE request"""

        request_name = name if name else self.request_name

        return HttpSession(**self.session_info).delete(url=url, name=request_name, **kwargs)

    def get(self, url, name=None, **kwargs):
        """Sends a GET request"""

        request_name = name if name else self.request_name

        return HttpSession(**self.session_info).get(url=url, name=request_name, **kwargs)

    def head(self, url, name=None, **kwargs):
        """Sends a HEAD request"""

        request_name = name if name else self.request_name

        return HttpSession(**self.session_info).head(url=url, name=request_name, **kwargs)

    def options(self, url, name=None, **kwargs):
        """Sends a OPTIONS request"""

        request_name = name if name else self.request_name

        return HttpSession(**self.session_info).options(url=url, name=request_name, **kwargs)

    def patch(self, url, data=None, name=None, **kwargs):
        """Sends a PATCH request"""

        request_name = name if name else self.request_name

        return HttpSession(**self.session_info).patch(url=url, data=data, name=request_name, **kwargs)

    def post(self, url, data=None, name=None, **kwargs):
        """Sends a POST request"""

        request_name = name if name else self.request_name

        return HttpSession(**self.session_info).post(url=url, data=data, name=request_name, **kwargs)

    def put(self, url, data=None, name=None, **kwargs):
        """Sends a PUT request"""

        request_name = name if name else self.request_name

        return HttpSession(**self.session_info).put(url=url, data=data, name=request_name, **kwargs)

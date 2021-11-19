"""
Connection pools can be used to pad out the number of ports occupied by each user.
This is potentially useful in low user count high throughput scenarios, where the
target load balancer may not behaving as expected.

Follow up information on Azure:
https://docs.microsoft.com/en-us/azure/load-balancer/distribution-mode-concepts
Follow up information on AWS:
https://docs.aws.amazon.com/AmazonECS/latest/developerguide/load-balancer-types.html
"""

from locust import FastHttpUser, HttpUser, events
from locust.clients import HttpSession
from locust.contrib.fasthttp import FastHttpSession
from itertools import cycle
from argparse import ArgumentParser
from typing import Optional, List


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

        for _ in range(self.size):
            self._pool.append(
                FastHttpSession(
                    user.environment,  # type: ignore
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

    def delete(self, path, **kwargs):
        """sends a DELETE request"""
        return next(self.pool).delete(path, **kwargs)

    def get(self, path, **kwargs):
        """Sends a GET request"""
        return next(self.pool).get(path, **kwargs)

    def head(self, path, **kwargs):
        """Sends a HEAD request"""
        return next(self.pool).head(path, **kwargs)

    def options(self, path, **kwargs):
        """Sends a OPTIONS request"""
        return next(self.pool).options(path, **kwargs)

    def patch(self, path, data=None, **kwargs):
        """Sends a PATCH request"""
        return next(self.pool).patch(path, data=data, **kwargs)

    def post(self, path, data=None, **kwargs):
        """Sends a POST request"""
        return next(self.pool).post(path, data=data, **kwargs)

    def put(self, path, data=None, **kwargs):
        """Sends a PUT request"""
        return next(self.pool).put(path, data=data, **kwargs)


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

        for _ in range(self.size):
            self._pool.append(
                HttpSession(
                    base_url=user.host, request_event=user.environment.events.request, user=user  # type: ignore
                )
            )

        self.pool = cycle(self._pool)

    def delete(self, url, **kwargs):
        """sends a DELETE request"""
        return next(self.pool).delete(url=url, **kwargs)

    def get(self, url, **kwargs):
        """Sends a GET request"""
        return next(self.pool).get(url=url, **kwargs)

    def head(self, url, **kwargs):
        """Sends a HEAD request"""
        return next(self.pool).head(url=url, **kwargs)

    def options(self, url, **kwargs):
        """Sends a OPTIONS request"""
        return next(self.pool).options(url=url, **kwargs)

    def patch(self, url, data=None, **kwargs):
        """Sends a PATCH request"""
        return next(self.pool).patch(url=url, data=data, **kwargs)

    def post(self, url, data=None, **kwargs):
        """Sends a POST request"""
        return next(self.pool).post(url=url, data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        """Sends a PUT request"""
        return next(self.pool).put(url=url, data=data, **kwargs)

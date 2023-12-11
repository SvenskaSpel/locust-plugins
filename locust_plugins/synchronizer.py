from typing import Dict, Iterator, Type, Optional
import logging
from gevent.event import AsyncResult
from locust import User, events

from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

results: Dict[int, AsyncResult] = {}
iterator: Optional[Iterator[Dict]] = None


def register(environment: Environment, reader: Optional[Iterator[dict]]):
    """Register synchronizer method handlers and tie them to use the iterator that you pass.

    reader is not used on workers, so you can leave it as None there.
    """
    global iterator
    iterator = reader

    runner = environment.runner
    if not reader and not isinstance(runner, WorkerRunner):
        raise Exception("reader is a mandatory parameter when not on a worker runner")
    if runner:
        # called on master
        def user_request(environment: Environment, msg, **kwargs):
            assert iterator
            data = next(iterator)
            environment.runner.send_message(
                "synchronizer_response",
                {"payload": data, "user_id": msg.data["user_id"]},
                client_id=msg.data["client_id"],
            )

        # called on worker
        def user_response(environment: Environment, msg, **kwargs):
            results[msg.data["user_id"]].set(msg.data)

        if not isinstance(runner, WorkerRunner):
            runner.register_message("synchronizer_request", user_request)
        if not isinstance(runner, MasterRunner):
            runner.register_message("synchronizer_response", user_response)


def getdata(user: User) -> Dict:
    """Get the next data dict from reader

    Args:
        u (User): current user object (we use the object id of the user to keep track of who's waiting for which data)
    """
    if not user.environment.runner:  # no need to do anything clever if there is no runner
        return next(iterator)

    if id(user) in results:
        logging.warning("This user was already waiting for data. Strange.")

    results[id(user)] = AsyncResult()
    runner = user.environment.runner
    runner.send_message("synchronizer_request", {"user_id": id(user), "client_id": runner.client_id})
    data = results[id(user)].get()["payload"]  # this waits for the reply
    del results[id(user)]
    return data

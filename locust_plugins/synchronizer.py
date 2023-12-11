from typing import Dict, Iterator, Optional
import logging
from gevent.event import AsyncResult
from locust import User

from locust.env import Environment
from locust.runners import WorkerRunner

_results: Dict[int, AsyncResult] = {}
_iterator: Optional[Iterator[Dict]] = None


# received on master
def _synchronizer_request(environment: Environment, msg, **kwargs):
    assert _iterator
    data = next(_iterator)
    environment.runner.send_message(
        "synchronizer_response",
        {"payload": data, "user_id": msg.data["user_id"]},
        client_id=msg.data["client_id"],
    )


# received on worker
def _synchronizer_response(environment: Environment, msg, **kwargs):
    _results[msg.data["user_id"]].set(msg.data)


def register(environment: Environment, reader: Optional[Iterator[dict]]):
    """Register synchronizer method handlers and tie them to use the iterator that you pass.

    reader is not used on workers, so you can leave it as None there.
    """
    global _iterator
    _iterator = reader

    runner = environment.runner
    if not reader and not isinstance(runner, WorkerRunner):
        raise Exception("reader is a mandatory parameter when not on a worker runner")
    if runner:
        runner.register_message("synchronizer_request", _synchronizer_request)
        runner.register_message("synchronizer_response", _synchronizer_response)


def getdata(user: User) -> Dict:
    """Get the next data dict from reader

    Args:
        user (User): current user object (we use the object id of the User to keep track of who's waiting for which data)
    """
    if not user.environment.runner:  # no need to do anything clever if there is no runner
        return next(_iterator)

    if id(user) in _results:
        logging.warning("This user was already waiting for data. Strange.")

    _results[id(user)] = AsyncResult()
    runner = user.environment.runner
    runner.send_message("synchronizer_request", {"user_id": id(user), "client_id": runner.client_id})
    data = _results[id(user)].get()["payload"]  # this waits for the reply
    del _results[id(user)]
    return data

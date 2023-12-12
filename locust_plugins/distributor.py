from typing import Dict, Iterator, Optional
import logging
from gevent.event import AsyncResult
from locust import User

from locust.env import Environment
from locust.runners import WorkerRunner

_results: Dict[int, AsyncResult] = {}
_iterator: Optional[Iterator[Dict]] = None


# received on master
def _distributor_request(environment: Environment, msg, **kwargs):
    data = next(_iterator)
    environment.runner.send_message(
        "distributor_response",
        {"payload": data, "user_id": msg.data["user_id"]},
        client_id=msg.data["client_id"],
    )


# received on worker
def _distributor_response(environment: Environment, msg, **kwargs):
    _results[msg.data["user_id"]].set(msg.data)


def register(environment: Environment, iterator: Optional[Iterator[dict]]):
    """Register distributor method handlers and tie them to use the iterator that you pass.

    iterator is not used on workers, so you can leave it as None there.
    """
    global _iterator
    _iterator = iterator

    runner = environment.runner
    assert iterator or isinstance(runner, WorkerRunner), "iterator is a mandatory parameter when not on a worker runner"
    if runner:
        runner.register_message("distributor_request", _distributor_request)
        runner.register_message("distributor_response", _distributor_response)


def getdata(user: User) -> Dict:
    """Get the next data dict from iterator

    Args:
        user (User): current user object (we use the object id of the User to keep track of who's waiting for which data)
    """
    if not user.environment.runner:  # no need to do anything clever if there is no runner
        assert _iterator, "Did you forget to call register() before trying to get data?"
        return next(_iterator)

    if id(user) in _results:
        logging.warning("This user was already waiting for data. Strange.")

    _results[id(user)] = AsyncResult()
    runner = user.environment.runner
    runner.send_message("distributor_request", {"user_id": id(user), "client_id": runner.client_id})
    data = _results[id(user)].get()["payload"]  # this waits for the reply
    del _results[id(user)]
    return data

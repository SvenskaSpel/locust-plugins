from typing import Dict, Iterator, Type, Optional
import logging
from gevent.event import AsyncResult
from locust import User, events

from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

test_data: Dict[int, AsyncResult] = {}
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
            assert iterator  # should have been instantiated by now...
            data = next(iterator)
            # data["_id"] = str(data["_id"])  # this is an ObjectId, msgpack doesnt know how to serialize it
            environment.runner.send_message(
                "synchronizer_response",
                {"payload": data, "user_id": msg.data["user_id"]},
                client_id=msg.data["client_id"],
            )

        # called on worker
        def user_response(environment: Environment, msg, **kwargs):
            test_data[msg.data["user_id"]].set(msg.data)

        if not isinstance(runner, WorkerRunner):
            runner.register_message("synchronizer_request", user_request)
        if not isinstance(runner, MasterRunner):
            runner.register_message("synchronizer_response", user_response)


def getdata(u: User) -> Dict:
    if not u.environment.runner:  # no need to do anything clever if there is no runner
        return next(iterator)

    if id(u) in test_data:
        logging.warning("This user was already waiting for data. Not sure how to handle this nicely...")

    test_data[id(u)] = AsyncResult()
    runner = u.environment.runner
    runner.send_message("synchronizer_request", {"user_id": id(u), "client_id": runner.client_id})
    data = test_data[id(u)].get()["payload"]
    del test_data[id(u)]
    return data

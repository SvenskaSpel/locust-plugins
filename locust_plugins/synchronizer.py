from typing import Dict, Iterator, Type, Optional
import logging
from gevent.event import AsyncResult
from locust import User, events

from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

test_data: Dict[int, AsyncResult] = {}
iterator: Optional[Iterator[Dict]] = None


def register(i: Optional[Iterator[dict]], reader_class: Optional[Type[Iterator[Dict]]] = None, *args, **kwargs):
    """Register synchronizer methods and tie them to use the iterator that you pass.

    To avoid unnecessarily instantiating the iterator on workers (where it isnt used),
    you can pass an iterator class and initialization parameters instead of an object instance.
    """
    global iterator
    iterator = i

    @events.test_start.add_listener
    def test_start(environment, **_kw):
        global iterator
        runner = environment.runner
        if not i and not isinstance(runner, WorkerRunner):
            assert reader_class
            logging.debug(f"about to initialize reader class {reader_class}")
            iterator = reader_class(*args, **kwargs)
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


def getdata(u: User):
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

from typing import Dict, Iterator
import logging
from gevent.event import AsyncResult
from locust import User, events

# from locust.exception import StopUser
from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

test_data: Dict[int, AsyncResult] = {}
iterator: Iterator[Dict] = None


def register(i: Iterator[dict]):
    global iterator
    iterator = i

    @events.test_start.add_listener
    def test_start(environment, **_kw):
        runner = environment.runner
        if runner:
            # called on master
            def user_request(environment: Environment, msg, **kwargs):
                data = next(iterator)
                # data["_id"] = str(data["_id"])  # this is an ObjectId, msgpack doesnt know how to serialize it
                environment.runner.send_message(
                    "synchronizer_response",
                    {"payload": data, "user_id": msg.data["user_id"]},
                    client_id=msg.data["client_id"],
                )

            # called on worker
            def user_response(environment: Environment, msg, **kwargs):
                assert test_data
                test_data[msg.data["user_id"]].set(msg.data)

            if not isinstance(runner, WorkerRunner):
                runner.register_message("synchronizer_request", user_request)
            if not isinstance(runner, MasterRunner):
                runner.register_message("synchronizer_response", user_response)


def getdata(u: User):
    # try:
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
    # except KeyboardInterrupt:
    #     # probably we're just shutting down but lets try to be as graceful as possible
    #     logging.debug("Caught SIGINT"
    #     raise StopUser()

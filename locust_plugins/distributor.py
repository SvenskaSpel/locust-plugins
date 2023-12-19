from typing import Dict, Iterator, Optional
import logging
from gevent.event import AsyncResult
import greenlet
import gevent
from locust.env import Environment
from locust.runners import WorkerRunner

_results: Dict[int, AsyncResult] = {}


class Distributor(Iterator):
    def __init__(self, environment: Environment, iterator: Optional[Iterator], name="distributor"):
        """Register distributor method handlers and tie them to use the iterator that you pass.

        iterator is not used on workers, so you can leave it as None there.
        """
        self.iterator = iterator
        self.name = name
        self.runner = environment.runner
        assert iterator or isinstance(
            self.runner, WorkerRunner
        ), "iterator is a mandatory parameter when not on a worker runner"
        if self.runner:
            # received on master
            def _distributor_request(environment: Environment, msg, **kwargs):
                # do this in the background to avoid blocking locust's client_listener loop
                gevent.spawn(self._master_next_and_send, msg.data["gid"], msg.data["client_id"])

            # received on worker
            def _distributor_response(environment: Environment, msg, **kwargs):
                _results[msg.data["gid"]].set(msg.data)

            self.runner.register_message(f"_{name}_request", _distributor_request)
            self.runner.register_message(f"_{name}_response", _distributor_response)

    def _master_next_and_send(self, gid, client_id):
        item = next(self.iterator)
        self.runner.send_message(
            f"_{self.name}_response",
            {"item": item, "gid": gid},
            client_id=client_id,
        )

    def __next__(self):
        """Get the next data dict from iterator

        Args:
            user (User): current user object (we use the object id of the User to keep track of who's waiting for which data)
        """
        if not self.runner:  # no need to do anything clever if there is no runner
            assert self.iterator
            return next(self.iterator)

        gid = greenlet.getcurrent().minimal_ident  # type: ignore

        if gid in _results:
            logging.warning("This user was already waiting for data. Strange.")

        _results[gid] = AsyncResult()
        self.runner.send_message(f"_{self.name}_request", {"gid": gid, "client_id": self.runner.client_id})
        item = _results[gid].get()["item"]  # this waits for the reply
        del _results[gid]
        return item

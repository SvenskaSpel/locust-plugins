from typing import Iterator, Optional, Dict
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from datetime import datetime, timezone
import logging
import time
from contextlib import contextmanager
import os
from os import environ as env
from abc import ABC, abstractmethod
from gevent.lock import Semaphore

dblock = Semaphore()


class MongoLRUReader(Iterator[Dict]):
    def __init__(
        self,
        filter: Dict,  # pylint: disable=redefined-builtin
        timestamp_field: str,
        coll: Optional[Collection] = None,
    ):
        """A thread safe iterator to read test data from a mongo collection sorted by least-recently-used.

        Order is ensured even if Locust is restarted, because the timestamp_field is updated on every iteration step.

        Iteration is quite fast, but the first query can be slow if you dont have an index that covers the filter and sort fields.

        Args:
            filter (Dict): Query filter statement
            sort_field (str): Time stamp field, e.g. "last_used"
            collection (pymongo.collection.Collection, optional): By default, we use LOCUST_MONGO, LOCUST_MONGO_DATABASE and LOCUST_MONGO_COLLECTION env vars to get the collection, but you can also pass a pre-existing Collection.

        """
        self.timestamp_field = timestamp_field
        if coll is None:
            self.coll: Collection = MongoClient(env["LOCUST_MONGO"])[env["LOCUST_MONGO_DATABASE"]][
                env["LOCUST_MONGO_COLLECTION"]
            ]
        else:
            self.coll = coll
        self.cursor: Cursor = self.coll.find(filter, sort=[(self.timestamp_field, 1)])
        records_in_buffer = self.cursor._refresh()  # trigger fetch immediately instead of waiting for the first next()
        if not records_in_buffer:
            logging.warning(f"No records returned from query {filter}")

    def __next__(self) -> dict:
        try:
            with dblock:
                doc: dict = next(self.cursor)
            self.coll.update_one(
                {"_id": doc["_id"]},
                {"$set": {self.timestamp_field: datetime.now(tz=timezone.utc)}},
            )
            return doc
        except StopIteration:
            with dblock:
                self.cursor.rewind()
            return next(self.cursor)


### Legacy


class NoUserException(Exception):
    pass


class User(dict):
    def __init__(self, coll: Collection, query: dict):
        self.coll = coll
        with dblock:
            data = self.coll.find_one_and_update(
                query,
                {"$set": {"last_login": datetime.now(tz=timezone.utc), "logged_in": True}},
                sort=[("last_login", 1)],
            )
        if not data:
            raise NoUserException(f"Didnt get any user from db ({self.coll}) using query {query}")
        super().__init__(data)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.coll.find_one_and_update({"_id": self["_id"]}, {"$set": {key: value}})

    def __delitem__(self, key):
        super().__delitem__(key)
        self.coll.find_one_and_update({"_id": self["_id"]}, {"$unset": {key: 1}})


class AbstractReader(ABC):
    @abstractmethod
    @contextmanager
    def user(self, query: dict = None) -> Iterator[User]:
        pass


class MongoReader(AbstractReader):
    def __init__(self, uri=None, database=None, collection=None, filters=[]):
        uri = uri or os.environ["LOCUST_MONGO"]
        database = database or os.environ["LOCUST_MONGO_DATABASE"]
        collection = collection or os.environ["LOCUST_MONGO_COLLECTION"]
        self.coll = MongoClient(uri)[database][collection]
        self.filters = filters
        self.reduced_filters = []
        self.delay_warning = 0
        self.query = {"$and": filters + [{"logged_in": False}]}
        logging.warning("MongoReader is deprecated, please switch to MongoReaderLRU")

    @contextmanager
    def user(self, query: dict = None):
        start_at = time.monotonic()

        if not query:
            if not self.query:
                raise Exception("no query specified on object or as parameter :(")
            query = self.query

        user = User(self.coll, query)

        if start_at + self.delay_warning < time.monotonic():
            if not self.delay_warning:
                # dont warn on first query, just set the threshold
                self.delay_warning = 1
            else:
                logging.warning(
                    f"Getting a user took more than {self.delay_warning} seconds (doubling warning threshold for next time, query used was {query})"
                )
                self.delay_warning *= 2
        try:
            yield user
        finally:
            releasessn = self.coll.find_one_and_update(
                {"_id": user["_id"]},
                {"$set": {"logged_in": False}},
            )
        if releasessn is None:
            raise Exception(f"Couldnt release lock for user: {user}")

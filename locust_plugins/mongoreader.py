from typing import Iterator, Optional, Dict, List, Tuple
from pymongo import MongoClient
import pymongo.collection
from datetime import datetime, timezone
import logging
import time
from contextlib import contextmanager
import os
from abc import ABC, abstractmethod
from gevent.lock import Semaphore
from locust.runners import Runner, MasterRunner, WorkerRunner
from locust.env import Environment
from gevent.event import AsyncResult

dblock = Semaphore()


class SimpleMongoReader(Iterator[Dict]):
    "Read test data from mongo collection file using an iterator"

    def __init__(
        self,
        query: Optional[Dict] = None,
        sort_column=None,
        sort: List[Tuple[str, int]] = [],
        uri=None,
        database=None,
        collection=None,
    ):
        self.query = query
        self.sort_column = sort_column
        if self.sort_column:
            if sort:
                raise Exception("Dont set both sort column and sort")
            self.sort = [(self.sort_column, 1)]
        else:
            self.sort = sort
        self.uri = uri or os.environ["LOCUST_MONGO"]
        self.database = database or os.environ["LOCUST_MONGO_DATABASE"]
        self.collection = collection or os.environ["LOCUST_MONGO_COLLECTION"]
        self.coll = MongoClient(self.uri)[self.database][self.collection]
        self.cursor = self.coll.find(self.query, sort=self.sort)

    def __next__(self):
        try:
            with dblock:
                doc = next(self.cursor)
            if self.sort_column:
                self.coll.find_one_and_update(
                    {"_id": doc["_id"]},
                    {"$set": {self.sort_column: datetime.now(tz=timezone.utc)}},
                )
            return doc
        except StopIteration:
            with dblock:
                # there is a tiny chance the last find_one_and_update has not yet completed
                # so give it a little extra time so we dont accidentally get data that was just used
                if "w=0" in self.uri:
                    time.sleep(0.5)
                self.cursor = self.coll.find(self.query, sort=self.sort)
            return next(self.cursor)


class NoUserException(Exception):
    pass


class User(dict):
    def __init__(self, coll: pymongo.collection.Collection, query: dict):
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

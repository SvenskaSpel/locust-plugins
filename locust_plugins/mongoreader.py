from pymongo import MongoClient, ReturnDocument, errors
from datetime import datetime
import logging
import time
import os

connection_string = os.environ["LOCUST_MONGO"]
collection = os.environ["LOCUST_MONGO_COLLECTION"]
database = os.environ["LOCUST_MONGO_DATABASE"]


class MongoReader:
    def __init__(self, query):
        self.coll = MongoClient(connection_string)[database][collection]
        self._delay_warning = 0.5
        self._query = query

    # Get SSN and update customer as logged in
    def get(self):
        start_at = time.time()
        try:
            getOneUpdate = self.coll.find_one_and_update(
                self._query,
                {"$set": {"last_login": datetime.now(), "logged_in": 1}},
                sort=[("last_login", 1)],
                return_document=ReturnDocument.AFTER,
            )
            if getOneUpdate is None:
                raise Exception(f"Didnt get any customer from db. ")
            else:
                if start_at + self._delay_warning < time.time():
                    logging.warning(
                        f"Getting a customer took more than {self._delay_warning} seconds (doubling warning threshold for next time)"
                    )
                    self._delay_warning *= 2
                return getOneUpdate
        except Exception as e:
            raise errors.PyMongoError(e)

    # Set customer to not logged in
    def release_ssn(self, ssn):
        start_at = time.time()
        try:
            releasessn = self.coll.find_one_and_update(
                {"ssn": ssn}, {"$set": {"logged_in": 0}}, return_document=ReturnDocument.AFTER
            )
            if releasessn is None:
                raise Exception(f"Didnt update customer in db. ")
            else:
                if start_at + self._delay_warning < time.time():
                    logging.warning(
                        f"Logout customer took more than {self._delay_warning} seconds (doubling warning threshold for next time)"
                    )
                    self._delay_warning *= 2
                return releasessn
        except Exception as e:
            raise errors.PyMongoError(e)

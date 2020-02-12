from pymongo import MongoClient
from datetime import datetime
import logging
import time
import os
from contextlib import contextmanager

connection_string = os.environ["LOCUST_MONGO"]
collection = os.environ["LOCUST_MONGO_COLLECTION"]
database = os.environ["LOCUST_MONGO_DATABASE"]


class MongoReader:
    def __init__(self, filters):
        self.coll = MongoClient(connection_string)[database][collection]
        self.delay_warning = 0.5
        self.query = {"$and": filters + [{"logged_in": 1}]}

    @contextmanager
    def customer(self):
        start_at = time.time()
        customer = self.coll.find_one_and_update(
            self.query, {"$set": {"last_login": datetime.now(), "logged_in": 1}}, sort=[("last_login", 1)]
        )
        if start_at + self.delay_warning < time.time():
            logging.warning(
                f"Getting a customer took more than {self.delay_warning} seconds (doubling warning threshold for next time)"
            )
            self.delay_warning *= 2
        if customer is None:
            raise Exception(f"Didnt get any customer from db")
        try:
            yield customer
        finally:
            releasessn = self.coll.find_one_and_update(
                {"$and": [{"ssn": customer["ssn"]}, {"logged_in": 1}]}, {"$set": {"logged_in": 0}},
            )
        if releasessn is None:
            raise Exception(f"Couldnt release lock for customer in db. ")

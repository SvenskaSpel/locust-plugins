import os
from locust_plugins.mongoreader import MongoReader
from locust import HttpUser, task

reader = MongoReader(
    filters=[{"tb": 0}, {"lb": 1}],
    uri=os.environ["LOCUST_MONGO"],
    database=os.environ["LOCUST_MONGO_DATABASE"],
    collection=os.environ["LOCUST_MONGO_COLLECTION"],
)


class MyUser(HttpUser):
    @task
    def my_task(self):
        with reader.user() as user:
            self.client.get(f"/?ssn={user['ssn']}")  # use data from db to make request
            user["foo"] = "bar"  # add/update field in db (for use some other time)

    host = "http://example.com"

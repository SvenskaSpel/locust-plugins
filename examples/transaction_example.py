from locust import HttpUser, task, between, SequentialTaskSet
from locust_plugins.transaction_manager import TransactionManager

        
from locust import HttpUser, SequentialTaskSet, task, between, events
import logging

import json, random, string

class MakePurchase(SequentialTaskSet):
    
    def on_start(self):
        self.purchase_id = get_uuid()

    @task
    def home(self):
        self.startup = tm.start_transaction("startup")
        self.client.get("/", name ="01 /")

    @task
    def get_config_json(self):
        response = self.client.get("/config.json", name="02 /config.json")
        response_json = json.loads(response.text)
        self.api_host = response_json["API_URL"]
        tm.end_transaction(self.startup)

    @task
    def get_item(self):
        self.make_purchase = tm.start_transaction("make_purchase")
        response = self.client.get(self.api_host + "/entries", name="03 /entries")
        response_json = json.loads(response.text)
        self.id = response_json["Items"][0]["id"]

    @task
    def view_product(self):
        self.user_cookie = get_uuid()
        self.client.cookies["user"] = self.user_cookie
        response = self.client.get("/prod.html?idp_=" + str(self.id), name="04 /prod.html?idp_")

    @task
    def view(self):
        payload = '{"id":"' + str(self.id) + '"}'
        response = self.client.post(self.api_host + "/view", payload , headers={"Content-Type": "application/json"}, name="05 /view")

    @task
    def add_to_cart(self):
        payload = '{"id":"' + self.purchase_id + '","cookie":"user=' + self.user_cookie + '","prod_id":' + str(self.id) + ',"flag":false}'
        response = self.client.post(self.api_host + "/addtocart", payload, headers={"Content-Type": "application/json"},  name="06 /addtocart")

    @task
    def view_cart(self):
        response = self.client.get("/cart.html", name="07 /cart.html")

    @task
    def post_cart(self):
        payload = '{"cookie":"user=' + self.user_cookie + '","flag":false}'
        response = self.client.post(self.api_host + "/viewcart", payload, headers={"Content-Type": "application/json"},  name="08 /viewcart")
        tm.end_transaction(self.make_purchase)

    @task
    def delete_item(self):
        payload = '{"cookie":"user=' + self.user_cookie + '"}'
        with self.client.post(self.api_host + "/deletecart", payload, headers={"Content-Type": "application/json"},  name="09 /deletecart", catch_response=True) as response:
            if response.content != b"Delete complete":
                response.failure("delete incomplete")

class DemoBlazePurchaser(HttpUser):
    wait_time = between(2, 5)
    tasks = [MakePurchase]

def get_uuid():
    #make a random string
    r_s = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    #return it in a 'uuid' format
    uuid = r_s[:8] + "-" + r_s[8:12] + "-" + r_s[12:16] + "-" + r_s[16:20] + "-" + r_s[20:32]
    return uuid


tm = TransactionManager()


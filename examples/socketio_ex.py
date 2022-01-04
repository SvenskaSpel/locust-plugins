import time
import json
from locust import task
from locust_plugins.users import SocketIOUser


class MySocketIOUser(SocketIOUser):
    @task
    def my_task(self):
        self.my_value = None

        self.connect("wss://example.com/socket.io/?EIO=3&transport=websocket")

        # example of subscribe
        self.send('42["subscribe",{"url":"/sport/matches/11995208/draws","sendInitialUpdate": true}]')

        # wait until I get a push message to on_message
        while not self.my_value:
            time.sleep(0.1)

        # wait for additional pushes, while occasionally sending heartbeats, like a real client would
        self.sleep_with_heartbeat(10)

    def on_message(self, message):
        self.my_value = json.loads(message)["my_value"]

    if __name__ == "__main__":
        host = "http://example.com"

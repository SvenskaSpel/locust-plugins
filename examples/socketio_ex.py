from locust import task
from locust_plugins.users import SocketIOUser


class MySocketIOUser(SocketIOUser):
    @task
    def my_task(self):
        # example of subscribe
        self.send('42["subscribe",{"url":"/sport/matches/11995208/draws","sendInitialUpdate": true}]')
        # you can do http in the same taskset as well
        self.client.get("/")
        # wait for pushes, while occasionally sending heartbeats, like a real client would
        self.sleep_with_heartbeat(10)

    if __name__ == "__main__":
        host = "http://example.com"

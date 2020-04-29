from locust import task
from locust_plugins.users import SocketIOUser
from locust.wait_time import constant


class MySocketIOUser(SocketIOUser):
    @task
    def my_task(self):
        # example of subscribe
        self.locust.send('42["subscribe",{"url":"/sport/matches/11995208/draws","sendInitialUpdate": true}]')
        # you can do http in the same taskset as well
        self.client.get("/")
        # wait for pushes, while occasionally sending heartbeats, like a real client would
        self.locust.sleep_with_heartbeat(10)

    wait_time = constant(0)
    if __name__ == "__main__":
        host = "http://example.com"

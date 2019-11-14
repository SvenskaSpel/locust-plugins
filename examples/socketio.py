from locust import task
from locust.core import TaskSet
from locust_plugins.locusts import SocketIOLocust
from locust.wait_time import constant


class UserBehaviour(TaskSet):
    @task
    def my_task(self):
        # example of subscribe
        self.locust.send('42["subscribe",{"url":"/sport/matches/11995208/draws","sendInitialUpdate": true}]')
        # you can do http in the same taskset as well
        self.client.get("/")
        # wait for pushes, while occasionally sending heartbeats, like a real client would
        self.locust.sleep_with_heartbeat(10)


class MySocketIOLocust(SocketIOLocust):
    task_set = UserBehaviour
    wait_time = constant(0)
    if __name__ == "__main__":
        host = "http://example.com"

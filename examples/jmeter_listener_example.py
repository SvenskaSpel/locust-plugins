from locust import HttpUser, TaskSet, task, between
from locust_plugins.jmeter_listener import JmeterListener

def index(l):
    l.client.get("/")

def stats(l):
    l.client.get("/stats/requests")

class UserTasks(TaskSet):
    # one can specify tasks like this
    tasks = [index, stats]
    
    # but it might be convenient to use the @task decorator
    @task
    def page404(self):
        self.client.get("/does_not_exist")
    
class WebsiteUser(HttpUser):
    """
    User class that does requests to the locust web server running on localhost
    """
    host = "http://localhost:8089"
    wait_time = between(2, 5)
    tasks = [UserTasks]

    def on_start(self):
        jmeter_listener.add_user()
        jmeter_listener.set_user_name(self.__class__.__name__)

jmeter_listener = JmeterListener()
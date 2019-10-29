import json
import logging
import re
import subprocess
import time

import gevent
import websocket
from locust import HttpLocust, Locust
from locust.events import request_success
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WebdriverLocust(Locust):
    """
    A locust that includes a Webdriver client.
    Download & launch selenium server first:
    https://www.seleniumhq.org/download/
    java -jar selenium-server-standalone-3.141.59.jar
    """

    # kill old webdriver browser instances
    subprocess.Popen(["killall", "chromedriver"])
    subprocess.Popen(["pkill", "-f", " --test-type=webdriver"])

    def __init__(self, headless=True):
        super(WebdriverLocust, self).__init__()
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        self.client = webdriver.Remote(
            command_executor="http://127.0.0.1:4444/wd/hub", desired_capabilities=chrome_options.to_capabilities()
        )


class SocketIOLocust(HttpLocust):
    """
    A locust that includes a socket io websocket connection.
    You could easily use this a template for a pure WS taskset,
    socket.io just happens to be my use case
    """

    def __init__(self):
        super(SocketIOLocust, self).__init__()
        ws_host = re.sub(r"https*://", "", self.host)
        self.ws = websocket.create_connection(f"wss://{ws_host}/socket.io/?EIO=3&transport=websocket")
        gevent.spawn(self.receive)

    def receive(self):
        message_regex = re.compile(r"(\d*)(.*)")
        description_regex = re.compile(r"<([0-9]+)>$")
        response_time = None
        while True:
            message = self.ws.recv()
            logging.debug(f"WSR: {message}")
            m = message_regex.match(message)
            code = m.group(1)
            json_string = m.group(2)
            if code == "0":
                name = "0 open"
            elif code == "3":
                name = "3 heartbeat"
            elif code == "40":
                name = "40 message ok"
            elif code == "42":
                # this is rather specific to our use case. Some messages contain an originating timestamp,
                # and we use that to calculate the delay & report it as locust response time
                # see it as inspiration rather than something you just pick up and use
                obj = json.loads(json_string)
                name = f"{code} {obj[0]} apiUri: {obj[1]['apiUri']}"
                if obj[1]["value"] != "":
                    description = obj[1]["value"]["draw"]["description"]
                    description_match = description_regex.search(description)
                    if description_match:
                        sent_timestamp = int(description_match.group(1))
                        current_timestamp = int(round(time.time() * 1000))
                        response_time = current_timestamp - sent_timestamp
                    else:
                        # differentiate samples that have no timestamps from ones that do
                        name += "_"
                else:
                    name += "_missingTimestamp"
            else:
                print(f"Received unexpected message: {message}")
                continue
            # Locust mail fail if no response time was detected (response_time = None)
            # There is a small locust patch in my fork, install it like this:
            # pip install -e git+https://github.com/cyberw/locust.git@allow-samples-with-None-response-time#egg=locustio
            request_success.fire(
                request_type="WSR", name=name, response_time=response_time, response_length=len(message)
            )

    def send(self, body):
        if body == "2":
            action = "2 heartbeat"
        else:
            m = re.search(r'(\d*)\["([a-z]*)"', body)
            code = m.group(1)
            action = m.group(2)
            url_part = re.search(r'"url": *"([^"]*)"', body)
            url = re.sub(r"/[0-9_]*/", "/:id/", url_part.group(1))
            action = f"{code} {action} url: {url}"

        request_success.fire(request_type="WSS", name=action, response_time=None, response_length=len(body))
        logging.debug(f"WSS: {body}")
        self.ws.send(body)

    def sleep_with_heartbeat(self, seconds):
        while seconds >= 0:
            gevent.sleep(min(15, seconds))
            seconds -= 15
            self.send("2")

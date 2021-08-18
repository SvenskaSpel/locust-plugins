import json
import logging
import re
import time
import gevent
import websocket
from locust import User


class SocketIOUser(User):
    """
    A locust that includes a socket io websocket connection.
    You could easily use this a template for plain WebSockets,
    socket.io just happens to be my use case. You can use multiple
    inheritance to combine this with an HttpUser
    (class MyUser(HttpUser, SocketIOUser)
    """

    abstract = True

    def connect(self, host: str, header: list):
        self.ws = websocket.create_connection(host, header=header)
        gevent.spawn(self.receive_loop)

    message_regex = re.compile(r"(\d*)(.*)")
    description_regex = re.compile(r"<([0-9]+)>$")

    def on_message(self, message):  # override this method in your subclass for custom handling
        m = self.message_regex.match(message)
        if m is None:
            # uh oh...
            raise Exception(f"got no matches in {message}")
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
            current_timestamp = time.time()
            obj = json.loads(json_string)
            logging.debug(json_string)
            ts_type, payload = obj
            name = f"{code} {ts_type} apiUri: {payload['apiUri']}"

            if payload["value"] != "":
                value = payload["value"]

                if "draw" in value:
                    description = value["draw"]["description"]
                    description_match = self.description_regex.search(description)
                    if description_match:
                        sent_timestamp = int(description_match.group(1))
                        response_time = current_timestamp - sent_timestamp
                    else:
                        # differentiate samples that have no timestamps from ones that do
                        name += "_"
                elif "source_ts" in value:
                    sent_timestamp = value["source_ts"]
                    response_time = (current_timestamp - sent_timestamp) * 1000
            else:
                name += "_missingTimestamp"
        else:
            print(f"Received unexpected message: {message}")
            return
        self.environment.events.request.fire(
            request_type="WSR",
            name=name,
            response_time=response_time,
            response_length=len(message),
            exception=None,
            context=self.context(),
        )

    def receive_loop(self):
        while True:
            message = self.ws.recv()
            logging.debug(f"WSR: {message}")
            self.on_message(message)

    def send(self, body, name=None, context={}):
        if not name:
            if body == "2":
                name = "2 heartbeat"
            else:
                # hoping this is a subscribe type message, try to detect name
                m = re.search(r'(\d*)\["([a-z]*)"', body)
                assert m is not None
                code = m.group(1)
                action = m.group(2)
                url_part = re.search(r'"url": *"([^"]*)"', body)
                assert url_part is not None
                url = re.sub(r"/[0-9_]*/", "/:id/", url_part.group(1))
                name = f"{code} {action} url: {url}"

        self.environment.events.request.fire(
            request_type="WSS",
            name=name,
            response_time=None,
            response_length=len(body),
            exception=None,
            context={**self.context(), **context},
        )
        logging.debug(f"WSS: {body}")
        self.ws.send(body)

    def sleep_with_heartbeat(self, seconds):
        while seconds >= 0:
            gevent.sleep(min(15, seconds))
            seconds -= 15
            self.send("2")

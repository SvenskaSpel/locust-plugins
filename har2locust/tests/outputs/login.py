#!/usr/bin/env python3
from locust import FastHttpUser, task, run_single_user, events
from locust_plugins.listeners import RescheduleTaskOnFail


class MyUser(FastHttpUser):
    host = "https://nowhere"
    default_headers = {
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "sv,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    }

    @task
    def t(self):
        self.client.post(
            "https://api.spela.test3.svenskaspel.se/player/1/authenticate/testlogin",
            headers={
                "accept": "application/json, text/javascript, */*; q=0.01",
                "content-type": "application/json",
                "origin": "https://spela.test3.svenskaspel.se",
            },
            data='{"personalId":"193804122491","source":3}',
        )
        self.client.get(
            "https://api.spela.test3.svenskaspel.se/player/1/customizedsettings?_=1636025335990",
            headers={
                "accept": "application/json, text/javascript, */*; q=0.01",
                "content-type": "text/plain",
                "origin": "https://spela.test3.svenskaspel.se",
            },
        )
        self.client.get(
            "https://spela.test3.svenskaspel.se/",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            },
        )
        self.client.get(
            "https://spela.test3.svenskaspel.se/logga-in/uppdaterade-villkor?returnUrl=%2F",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            },
        )
        self.client.post(
            "https://api.spela.test3.svenskaspel.se/player/1/terms",
            headers={
                "accept": "application/json, text/javascript, */*; q=0.01",
                "content-type": "application/json",
                "origin": "https://spela.test3.svenskaspel.se",
            },
            data="{}",
        )
        self.client.get(
            "https://api.spela.test3.svenskaspel.se/player/1/info?include=accountBalance&_=1636025343876",
            headers={
                "accept": "application/json, text/javascript, */*; q=0.01",
                "content-type": "text/plain",
                "origin": "https://spela.test3.svenskaspel.se",
            },
        )


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    RescheduleTaskOnFail(environment)


if __name__ == "__main__":
    run_single_user(MyUser)

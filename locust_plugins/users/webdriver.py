import subprocess
from locust import User
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WebdriverUser(User):
    """
    A locust that includes a Webdriver client.
    Download & launch selenium server first:
    https://www.seleniumhq.org/download/
    java -jar selenium-server-standalone-3.141.59.jar
    """

    abstract = True
    _first_instance = True

    def __init__(self, parent, headless=True):
        super().__init__(parent)
        if WebdriverUser._first_instance:
            WebdriverUser._first_instance = False
            # kill old webdriver browser instances
            subprocess.Popen(["killall", "chromedriver"])
            subprocess.Popen(["pkill", "-f", " --test-type=webdriver"])

        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        self.client = webdriver.Remote(
            command_executor="http://127.0.0.1:4444/wd/hub", desired_capabilities=chrome_options.to_capabilities()
        )

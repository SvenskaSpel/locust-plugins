from playwright.sync_api import sync_playwright, BrowserContext, Page
from locust import User

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)


class PlaywrightClient:
    def __init__(self, user: User):
        self.user = user
        self.context = browser.new_context()


class PlaywrightUser(User):
    abstract = True
    headless = False  # overwrite this as needed

    def __init__(self, parent):
        super().__init__(parent)
        self.context: BrowserContext = None
        self.page: Page = None

    def on_start(self):
        self.context = browser.new_context()
        self.page = self.context.new_page()

    def on_stop(self):
        self.page.close()
        self.context.close()

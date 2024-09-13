from unittest import TestCase
import importlib


class TestMissingExtras(TestCase):
    def test_error_messages(self):
        # This test is meant to be run after installing only basic locust_plugins
        for module in [
            "locust_plugins.listeners.timescale",
            "locust_plugins.listeners.appinsights",
            "locust_plugins.users.playwright",
            "locust_plugins.users.socketio",
            "locust_plugins.users.mqtt",
            "locust_plugins.users.kafka",
        ]:
            with self.assertLogs("root") as cm:
                with self.assertRaises(SystemExit):
                    importlib.import_module(module)
            self.assertIn('you need to install it using "pip install', cm.output[0])

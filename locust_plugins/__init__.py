__version__ = "0.0.45"

# Monkey patch User while waiting for everyone else to see the light:
# https://github.com/locustio/locust/issues/1308

from locust import User, constant

User.wait_time = constant(0)

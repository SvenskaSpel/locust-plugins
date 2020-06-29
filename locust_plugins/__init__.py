__version__ = "1.0.13"
import time
from .wait_time import constant_ips, constant_total_ips
from .debug import run_single_user

from locust import User, constant

# Monkey patch User while waiting for everyone else to see the light:
# https://github.com/locustio/locust/issues/1308
User.wait_time = constant(0)

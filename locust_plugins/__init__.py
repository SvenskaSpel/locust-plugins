__version__ = "1.0.14"
import time
from .wait_time import constant_ips, constant_total_ips
from .debug import run_single_user
from locust import User, constant
from . import checks as _checks  # import this for the side-effects

# Monkey patch User while waiting for everyone else to see the light:
# https://github.com/locustio/locust/issues/1308
User.wait_time = constant(0)

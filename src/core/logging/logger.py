import sys
import logging

logr = logging.getLogger(__name__)
logr.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logr.addHandler(handler)


def get_logr():
    return logr


def set_log_level(log_level: int):
    logr.setLevel(log_level)

# -*- coding: utf-8 -*-

"""Main module."""

import os
import logging
from functools import wraps

def environment(value):
    def environ_decorator(func):
        @wraps(func)
        def inner(*args):
            if value not in os.environ:
                logging.getLogger(__name__).error("Missing environment variable: %s" % (value))
                raise KeyError(value)
            return func(*args, os.environ[value])
        return inner
    return environ_decorator

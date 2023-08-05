# -*- coding: utf-8 -*-

"""Top-level package for @environment."""

__author__ = """Alexandr Mansurov"""
__email__ = 'alex@eghuro.cz'
__version__ = '0.2.0'

import os
import logging
from inspect import signature
from functools import wraps


class UnknownKeyword(BaseException):
    """Exception indicating unknown keyword was provided to @environment
       decorator in **kwargs.
    """
    pass


class EnvironMiss(KeyError):
    """Error indicating key is not present in environment."""
    pass


class DecoratorSyntaxError(BaseException):
    pass


def _missing(value):
    log = logging.getLogger(__name__)
    log.error("Missing environment variable: %s" % (value))
    raise EnvironMiss(value)


_allowed_keywords = ['onerror', 'in_self']


def environment(*value, **kwargs):
    """@environment decorator.

    Arguments:
       value   -- one or more environment tokens requested

       onerror -- optional function to be called if any of the environment
       tokens in value is not present in environment. Such function must take
       one parameter what is a string value of a missing environment token. If
       onerror is not set, error is logged and EnvironMiss exception is raised

       in_self -- optional variable name in case instance property is to be
       initialized. There must be only one value in such case.

    The decorator checks for presence of environment tokens and if successful
    reads their values to the function parameters of the decorated function
    after any called parameters provided.

    Eg. if calling function(a, b, c) that is decorated with @environment('X')
    the function must be defined as def function(a, b, c, x) and X from the
    environment is read as last parameter.

    When combining decorators or using multiple environment tokens in one
    @environment('X', 'Y', 'Z') the values are loaded from the left to the
    right, from the top to the bottom.

    If a function parameter for @environment is missing, when such function
    is called a TypeError is raised by the interpreter.
    """

    err = _missing

    if kwargs is not None:
        for k in kwargs:
            if k not in _allowed_keywords:
                raise UnknownKeyword(k)

        if 'onerror' in kwargs:
            err = kwargs['onerror']

    def environ_decorator(func):

        @wraps(func)
        def inner(*args):
            for v in value:
                if v not in os.environ:
                    err(v)
            if 'in_self' in kwargs:
                if len(value) != 1:
                    raise DecoratorSyntaxError(value)
                if 'self' not in signature(func).parameters:
                    raise DecoratorSyntaxError()
                args[0].__dict__[kwargs['in_self']] = os.environ[v]
                return func(*args)
            return func(*(list(args) + [os.environ[v] for v in value]))
        return inner
    return environ_decorator

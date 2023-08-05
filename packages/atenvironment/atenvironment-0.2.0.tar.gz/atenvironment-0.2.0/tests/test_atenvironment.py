#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `atenvironment` package."""


import unittest
import os
import random
import string
import itertools

from atenvironment import environment, UnknownKeyword, EnvironMiss, DecoratorSyntaxError


class TestAtenvironment(unittest.TestCase):
    """Tests for `atenvironment` package."""

    def test_decorator(self):
        """Test decorator."""
        key = next(iter(os.environ.keys()))

        @environment(key)
        def test(key):
            return key

        self.assertEqual(test(), os.environ[key])

    def test_noKey(self):
        """Test decorator with no key in environment."""
        for _ in range(7):
            # key = ''.join(random.choices(string.ascii_uppercase, k=random.randrange(42)))
            key = ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randrange(42)))
            if key not in os.environ:
                break

        self.assertFalse(key in os.environ)

        @environment(key)
        def test(key):
            return key

        self.assertRaises(EnvironMiss, test)

    def test_multiple(self):

        keys = tuple(itertools.islice(os.environ, 3))

        @environment(*keys)
        def test(a, b, c):
            return (a, b, c)

        self.assertEqual(tuple([os.environ[key] for key in keys]), test())

        keys = list(keys)
        @environment(*keys)
        def test(a, b, c):
            return (a, b, c)

        self.assertEqual(tuple([os.environ[key] for key in keys]), test())

    def test_multiple_miss(self):

        self.assertTrue('foobar' not in os.environ)
        keys = list(itertools.islice(os.environ, 3))
        keys.append('foobar')

        @environment(*keys)
        def test(a, b, c, d):
            return [a, b, c, d]

        self.assertRaises(EnvironMiss, test)

        keys = keys[:-1]
        @environment('foobar', *keys)
        def test(a,b,c,d):
            return [a, b, c, d]

        self.assertRaises(EnvironMiss, test)

    def test_onerror(self):
        self.assertTrue('foobar' not in os.environ)

        class TestResult(BaseException):
            pass

        def err(val):
            self.assertEqual('foobar', val)
            raise TestResult

        @environment('foobar', onerror=err)
        def test(a):
            return a

        self.assertRaises(TestResult, test)

    def test_onerror_multiple(self):
        class BodyExecuted(BaseException):
            pass

        class TestResultA(BaseException):
            pass

        class TestResultB(BaseException):
            pass

        def err0(x):
            raise TestResultA()

        def err1(x):
            raise TestResultB()

        self.assertTrue('foobar' not in os.environ)
        a0 = list(itertools.islice(os.environ, 3))
        a0.append('foobar')

        a1 = tuple(itertools.islice(os.environ, 3))

        @environment(*a0, onerror=err0)
        @environment(*a1, onerror=err1)
        def test(a, b, c, d, e, f):
            raise BodyExecuted()

        self.assertRaises(TestResultA, test)

        @environment(*a1, onerror=err0)
        @environment(*a0, onerror=err1)
        def test(a, b, c, d, e, f):
            raise BodyExecuted()

        self.assertRaises(TestResultB, test)

    def test_unknown_keyword(self):
        try:
            @environment(next(iter(os.environ.keys())), foobar=None)
            def test(a):
                return a
        except UnknownKeyword:
            pass
        else:
            self.assertTrue(False)

    def test_bad_signature(self):
        class BodyExecuted(BaseException):
            pass

        @environment(next(iter(os.environ.keys())))
        def test():
            raise BodyExecuted()

        self.assertRaises(TypeError, test)

    def test_class(self):
        x = next(iter(os.environ.keys()))
        class TestBed(object):
            @environment(x, in_self="foo")
            def __init__(self):
                pass

        t = TestBed()
        self.assertEqual(os.environ[x], t.foo)

    def test_class_only_one_key(self):
        keys = tuple(itertools.islice(os.environ, 3))

        class TestBed(object):
            @environment(*keys, in_self="foo")
            def __init__(self):
                raise BodyExecuted()

        try:
            TestBed()
        except DecoratorSyntaxError:
            pass
        else:
            self.assertTrue(False)

    def test_self_no_class(self):
        a1 = tuple(itertools.islice(os.environ, 1))
        @environment(*a1, in_self="foo")
        def test(a):
            raise BodyExecuted()
        try:
            test('a')
        except DecoratorSyntaxError:
            pass
        else:
            self.assertTrue(False)

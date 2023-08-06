from itertools import chain, count

from django.test import TestCase

from ..decorators import cache_function

i = count()


def func_no_args_no_cache():
    return next(i)


@cache_function(3600)
def func_no_args():
    return func_no_args_no_cache()


@cache_function(3600)
def func_args(*args):
    return ', '.join(chain([str(func_no_args_no_cache())], args[::-1]))


@cache_function(3600)
def func_kwargs(a, b):
    return ''.join([
        'a=',
        a,
        ' b=',
        b,
        str(func_no_args_no_cache()),
    ])


@cache_function(3600, key=lambda *args: sum(args))
def func_key(a, b):
    return func_no_args_no_cache()


class CacheFunctionTestCase(TestCase):
    def test_func_no_args(self):
        self.assertNotEqual(func_no_args_no_cache(), func_no_args_no_cache())
        self.assertEqual(func_no_args(), func_no_args())

    def test_func_args(self):
        self.assertEqual(func_args('a', 'b'), func_args('a', 'b'))
        self.assertNotEqual(func_args('a', 'b'), func_args('b', 'a'))

    def test_func_kwargs(self):
        self.assertEqual(func_kwargs(a='a', b='b'), func_kwargs(a='a', b='b'))
        self.assertNotEqual(func_kwargs('a', 'b'), func_kwargs(a='a', b='b'))

    def test_func_key(self):
        self.assertEqual(func_key(1, 2), func_key(1, 2))
        self.assertEqual(func_key(2, 1), func_key(1, 2))

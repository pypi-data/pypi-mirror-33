from functools import wraps
from itertools import chain

from django.core.cache import cache


def create_cache_key(func, args, kwargs):
    return '-'.join(
        map(
            str,
            chain(
                [func.__qualname__],
                args,
                map(':'.join, kwargs.items()),
            )
        )
    )


class cache_function:
    def __init__(self, timeout, key=None):
        self.timeout = timeout
        self.key = key

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = self.key
            if key is None:
                key = create_cache_key(func, args, kwargs)
            elif callable(key):
                key = create_cache_key(func, [key(*args, **kwargs)], {})
            data = cache.get(key)
            if data:
                return data
            data = func(*args, **kwargs)
            cache.set(key, data, self.timeout)
            return data
        return wrapper

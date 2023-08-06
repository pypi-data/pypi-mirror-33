import functools

from raven.contrib.django.raven_compat.models import client


def capture_exception(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            client.captureException()
            raise
    return wrapper

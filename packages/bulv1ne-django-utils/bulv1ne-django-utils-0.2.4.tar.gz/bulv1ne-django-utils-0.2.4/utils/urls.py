from django.conf import settings
from django.urls import reverse


def absolute_reverse(*args, site_url=None, **kwargs):
    if not site_url:
        site_url = settings.SITE_URL
    return ''.join([
        site_url,
        reverse(*args, **kwargs)
    ])

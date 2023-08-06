import logging

import requests

from django.core.cache import cache


def shorten(url):
    KEY = 'shorturl:{}'.format(url)
    logger = logging.getLogger(__name__)
    logger.info('Shortening url {}'.format(url))
    shorturl = cache.get(KEY)
    if shorturl:
        logger.info('Returning cached shorturl {}'.format(shorturl))
        return shorturl
    data = requests.get('https://is.gd/create.php', params={'format': 'json', 'url': url}).json()
    if 'shorturl' in data:
        shorturl = data['shorturl']
        logger.info('Shorturl: {}'.format(shorturl))
        # Store shorturl for 60 days
        cache.set(KEY, shorturl, 60 * 24 * 3600)
    else:
        logger.warning(data.get('errormessage', 'shorturl errormessage was not found'))
        # Store original url for 1 hour
        cache.set(KEY, url, 3600)
        return url
    return shorturl

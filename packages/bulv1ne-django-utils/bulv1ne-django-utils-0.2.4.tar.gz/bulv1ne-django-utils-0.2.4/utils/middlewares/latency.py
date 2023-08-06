import logging
import time


class LatencyMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        start_time = time.time()
        try:
            return self.get_response(request)
        finally:
            ds = int((time.time() - start_time) * 1000)
            self.logger.info('url: {} Latency {}ms'.format(request.build_absolute_uri(), ds))

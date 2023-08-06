from unittest.mock import MagicMock

from django.test import TestCase

from ..middlewares.latency import LatencyMiddleware


def get_response(request):
    return None


class Request:
    def build_absolute_uri(self):
        return 'http://example.com'


class LatencyMiddlewareTestCase(TestCase):

    def setUp(self):
        self.middleware = LatencyMiddleware(get_response)

    def test_success(self):
        self.middleware.logger.info = MagicMock()
        self.middleware(Request())
        self.middleware.logger.info.assert_called_with('url: http://example.com Latency 0ms')

from unittest.mock import patch

from django.test import TestCase

from ..raven import capture_exception


class RavenTestCase(TestCase):

    @capture_exception
    def func_success(self, arg1, kwarg2):
        return 'Good {} {}'.format(arg1, kwarg2)

    @capture_exception
    def func_fail(self):
        raise ValueError('Fail')

    def test_success(self):
        with patch('utils.raven.client.captureException') as mock:
            self.assertEqual(self.func_success('arg1', kwarg2='kwarg2'), 'Good arg1 kwarg2')
        self.assertFalse(mock.called)

    def test_fail(self):
        with patch('utils.raven.client.captureException') as mock:
            with self.assertRaises(ValueError):
                self.func_fail()
        self.assertTrue(mock.called)

from unittest.mock import patch

from django.test import TestCase

from ..mixins import SignedPkMixin
from ..signing import UrlSafeSigner, sign, unsign


class ExampleClass(SignedPkMixin):
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class SignedPkMixinTestCase(TestCase):
    def test_pk(self):
        obj = ExampleClass(pk='123')
        with patch('utils.mixins.unsign') as mock:
            self.assertEqual(obj.get_pk(), '123')
        self.assertFalse(mock.called)
        self.assertEqual(unsign(obj.get_pk_signed()), '123')

    def test_pk_signed(self):
        obj = ExampleClass(pk_signed=sign('123'))
        self.assertEqual(obj.get_pk(), '123')
        with patch('utils.mixins.unsign') as mock:
            self.assertEqual(unsign(obj.get_pk_signed()), '123')
        self.assertFalse(mock.called)

    def test_bad_base64(self):
        signer = UrlSafeSigner()
        pk_signed = str(signer.sign(123))
        self.assertIn('=', pk_signed)
        pk_signed = pk_signed.replace('=', '')
        self.assertEqual(signer.unsign(pk_signed), '123')

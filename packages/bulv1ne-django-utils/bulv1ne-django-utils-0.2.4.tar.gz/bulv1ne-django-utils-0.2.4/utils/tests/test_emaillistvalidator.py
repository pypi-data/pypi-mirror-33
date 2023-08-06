from django.core.exceptions import ValidationError
from django.test import TestCase

from ..validators import EmailListValidator


class EmailListValidatorTestCase(TestCase):
    def setUp(self):
        self.validator = EmailListValidator()

    def test_success(self):
        self.validator('foo@example.com bar@example.com')

    def test_fail(self):
        with self.assertRaisesRegex(ValidationError, '"bad" is not a valid email'):
            self.validator('bad foo@example.com')

import os
from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class PipelineTestCase(TestCase):
    def setUp(self):
        file_path = os.path.join(settings.STATIC_ROOT, 'staticfiles.json')
        if os.path.isfile(file_path):
            os.remove(file_path)

    def test_success(self):
        call_command('collectstatic', '--noinput', stdout=StringIO())
        call_command('clean_staticfilesjson', stdout=StringIO())

    def test_missing_staticfilesjson(self):
        with self.assertRaises(CommandError):
            call_command('clean_staticfilesjson', stdout=StringIO())

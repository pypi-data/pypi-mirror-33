import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        file_path = os.path.join(settings.STATIC_ROOT, 'staticfiles.json')
        if not os.path.isfile(file_path):
            raise CommandError('Could not find staticfiles.json')
        with open(file_path) as f:
            data = json.load(f)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)

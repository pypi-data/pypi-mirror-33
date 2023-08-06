import re

import yaml

FM_BOUNDARY = re.compile(r'^---$', re.MULTILINE)


def split(content):
    try:
        _, fm, body = FM_BOUNDARY.split(content, 2)
    except ValueError:
        raise ValueError('Invalid front matter content')
    try:
        fm_data = yaml.safe_load(fm)
    except yaml.scanner.ScannerError:
        raise ValueError('Invalid yaml')
    return [
        fm_data,
        body[1:],
    ]

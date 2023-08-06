from django.test import TestCase

from ..frontmatter import split


template = '''
---
key: value
foo:
  - bar
  - baz
---
Body content
'''

template_invalid = '''
---
- this
is
- invalid
---
'''

template_missing_frontmatter = '''
Nothing here
'''


class FrontmatterTestCase(TestCase):

    def test_success(self):
        data, body = split(template)
        self.assertEquals(data, {
            'key': 'value',
            'foo': ['bar', 'baz'],
        })
        self.assertEquals(body, 'Body content\n')

    def test_invalid_yaml(self):
        with self.assertRaisesRegex(ValueError, 'Invalid yaml'):
            split(template_invalid)

    def test_missing_frontmatter(self):
        with self.assertRaisesRegex(ValueError, 'Invalid front matter content'):
            split(template_missing_frontmatter)

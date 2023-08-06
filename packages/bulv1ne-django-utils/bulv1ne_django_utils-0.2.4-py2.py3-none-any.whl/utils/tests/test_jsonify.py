from django.template import Context, Template
from django.test import TestCase

template = '{% load jsonify %}{{ content | jsonify:2 }}'

template_html = '''[
  "foo",
  "bar",
  "ba<"
]'''


class MarkdownTestCase(TestCase):
    def test_markdown(self):
        data = {
            'content': [
                'foo',
                'bar',
                'ba<'
            ],
        }
        html = Template(template).render(Context(data))
        self.assertEqual(html, template_html)

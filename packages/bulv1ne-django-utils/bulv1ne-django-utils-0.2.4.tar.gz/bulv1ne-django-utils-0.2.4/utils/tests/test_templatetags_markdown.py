from django.template import Context, Template
from django.test import TestCase


template = '''
{% load md %}
{% markdown %}
# Foo
## Bar
Baz
{% endmarkdown %}
'''

template_html = '''
<h1>Foo</h1>
<h2>Bar</h2>
<p>Baz</p>
'''


class MarkdownTestCase(TestCase):
    def test_markdown(self):
        html = Template(template).render(Context({}))
        self.assertHTMLEqual(html, template_html)

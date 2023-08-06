from django.template import Context, Template
from django.test import TestCase

template_filter = '{% load md %}{{ content | markdown }}'
template_tag = '{% load md %}{% markdown %}{{ content }}{% endmarkdown %}'
template_tag_as = '{% load md %}{% markdown as my_variable %}{{ content }}{% endmarkdown %}'

content = '''
# My template

Some test
'''

content_html = '''
<h1>My template</h1>
<p>Some test</p>
'''.strip()


class MarkdownTestCase(TestCase):
    def test_filter(self):
        data = {
            'content': content
        }
        html = Template(template_filter).render(Context(data))
        self.assertEqual(html, content_html)

    def test_template_tag(self):
        data = {
            'content': content
        }
        html = Template(template_tag).render(Context(data))
        self.assertEqual(html, content_html)

    def test_template_tag_as(self):
        data = {
            'content': content
        }
        context = Context(data)
        html = Template(template_tag_as).render(context)
        self.assertEqual(html, '')
        self.assertIn('my_variable', context)
        self.assertEqual(context['my_variable'], content_html)

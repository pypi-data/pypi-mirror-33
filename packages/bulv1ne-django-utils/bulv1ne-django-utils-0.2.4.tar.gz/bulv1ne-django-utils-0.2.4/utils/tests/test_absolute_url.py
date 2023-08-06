from django.template import Context, Template
from django.test import TestCase

from utils.urls import absolute_reverse

template = '{% load absolute_url %}{% absolute_url "test" 1 %}'


class AbsoluteUrlTestCase(TestCase):
    def test_templatetags(self):
        html = Template(template).render(Context({}))
        self.assertEqual(html, 'http://www.example.com/test/1/')

    def test_function(self):
        url = absolute_reverse('test', args=[1])
        self.assertEqual(url, 'http://www.example.com/test/1/')

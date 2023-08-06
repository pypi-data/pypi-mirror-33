import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from markdown import markdown

register = template.Library()


@register.filter('markdown')
@stringfilter
def markdown_filter(value):
    return mark_safe(markdown(value))


@register.tag(name='markdown')
def do_markdown(parser, token):
    nodelist = parser.parse(('endmarkdown',))
    parser.delete_first_token()
    m = re.search(r'as (?P<var_name>\w+)$', token.contents)
    var_name = None
    if m:
        var_name = m.group('var_name')
    return MarkdownNode(nodelist, var_name)


class MarkdownNode(template.Node):
    def __init__(self, nodelist, var_name=None):
        self.nodelist = nodelist
        self.var_name = var_name

    def render(self, context):
        value = markdown_filter(self.nodelist.render(context))
        if self.var_name:
            context[self.var_name] = value
            return ''
        return value

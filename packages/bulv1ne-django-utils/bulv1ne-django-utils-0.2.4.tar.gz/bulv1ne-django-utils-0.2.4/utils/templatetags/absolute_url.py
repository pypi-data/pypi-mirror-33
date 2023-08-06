from django import template

from utils.urls import absolute_reverse

register = template.Library()


@register.simple_tag()
def absolute_url(viewname, *args, **kwargs):
    return absolute_reverse(viewname, args=args, kwargs=kwargs)

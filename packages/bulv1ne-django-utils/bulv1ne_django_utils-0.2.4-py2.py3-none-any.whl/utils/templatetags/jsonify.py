import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def jsonify(obj, indent=0):
    return mark_safe(json.dumps(obj, indent=indent))

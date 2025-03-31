from django import template

register = template.Library()

@register.filter
def has_attr(obj, attr):
    return hasattr(obj, attr) 
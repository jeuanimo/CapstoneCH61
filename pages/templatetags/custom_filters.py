"""Custom template tags for pages app"""
from django import template

register = template.Library()


@register.filter(name='split')
def split(value, arg):
    """
    Split a string by the given separator.
    Usage: {{ "tag1,tag2,tag3"|split:"," }}
    """
    if value:
        return value.split(arg)
    return []


@register.filter(name='strip')
def strip_filter(value):
    """
    Remove leading and trailing whitespace from a string.
    Usage: {{ " text "|strip }}
    """
    if value:
        return value.strip()
    return value

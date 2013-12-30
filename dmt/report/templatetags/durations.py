from django import template

register = template.Library()


@register.filter
def hours(value):
    return value.total_seconds() / 3600.0

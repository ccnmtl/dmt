from django import template
from django.utils.safestring import mark_safe
import dmt.main.utils as utils

register = template.Library()


@register.filter
def format_date(dt):
    """
    Takes a datetime and formats it like this:
      Tuesday, July 15, 2014
    """
    return dt.strftime('%A, %B %d, %Y')


@register.filter
def format_mdy(dt):
    """
    Takes a datetime and formats it like this:
      Jul. 15, 2014
    """
    return dt.strftime('%b. %d, %Y')


@register.filter
def interval_to_hours(duration):
    return utils.interval_to_hours(duration)


@register.filter(is_safe=True)
def markdown(value):
    return mark_safe(utils.commonmark_render(value))

from django import template
import dmt.main.utils as utils

register = template.Library()


@register.filter
def interval_to_hours(duration):
    return utils.interval_to_hours(duration)

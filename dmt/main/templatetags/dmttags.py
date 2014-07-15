from django import template

register = template.Library()


@register.filter
def interval_to_hours(duration):
    seconds = duration.total_seconds()
    hours = seconds / 3600
    if hours % 1 == 0:
        hours = int(hours)
    else:
        hours = round(hours, 2)
    return hours

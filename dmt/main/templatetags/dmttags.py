import bleach
from django import template
from html5lib.tokenizer import HTMLTokenizer
from dmt.main.models import InGroup
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
def linkify(value):
    return bleach.linkify(value,
                          skip_pre=True,
                          skip_code=True,
                          parse_email=False,
                          tokenizer=HTMLTokenizer)


@register.filter
def verbose_group_name(group_user):
    """Given a group's UserProfile, return its name."""
    return InGroup.verbose_name(group_user.fullname)

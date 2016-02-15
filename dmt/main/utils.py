import ntpath
import re
from simpleduration import Duration, InvalidDuration


def new_duration(timestr):
    try:
        d = Duration(timestr)
    except InvalidDuration:
        d = None

    # If the user's string is a number with no unit, simpleduration
    # throws an InvalidDuration exception. In this case, we'll assume
    # the user is talking about the number of hours.
    if d is None and re.match(r'\d+', timestr):
        try:
            d = Duration(timestr + 'h')
        except InvalidDuration:
            d = None

    if d is None:
        d = Duration('0 minutes')

    return d


def interval_to_hours(duration):
    """
    Takes a datetime.timedelta and returns the total hours as a
    user-presentable float.

    :rtype: int or float
    """
    if not hasattr(duration, 'total_seconds'):
        return 0

    seconds = duration.total_seconds()
    hours = seconds / 3600

    if hours % 1 == 0:
        hours = int(hours)
    else:
        hours = round(hours, 2)

    return hours


def safe_basename(s):
    """ take whatever crap the browser gives us,
    often something like "C:\fakepath\foo bar.png"
    and turn it into something suitable for our
    purposes"""
    # ntpath does the best at cross-platform basename extraction
    b = ntpath.basename(s)
    b = b.lower()
    # only allow alphanumerics, '-' and '.'
    b = re.sub(r'[^\w\-\.]', '', b)
    return b


def simpleduration_string(duration):
    """Returns a simpleduration-friendly string.

    Accepts a timedelta object.

    Based on Django's duration_string() function.
    """
    if duration is None:
        return ''

    days = duration.days
    seconds = duration.seconds

    minutes = seconds // 60
    seconds = seconds % 60

    hours = (minutes // 60) + (days * 24)
    minutes = minutes % 60

    string = ''
    if hours:
        string += '{:d}h '.format(hours)
    if minutes:
        string += '{:d}m '.format(minutes)
    if seconds:
        string += '{:d}s'.format(seconds)

    return string.strip()

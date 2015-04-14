import ntpath
import re
from simpleduration import Duration, InvalidDuration


def new_duration(timestr):
    try:
        d = Duration(timestr)
    except InvalidDuration:
        # eventually, this needs to get back to the user
        # via form validation, but for now
        # we just deal with it...
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

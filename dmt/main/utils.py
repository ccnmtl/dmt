import ntpath
import re


def interval_to_hours(duration):
    """
    Takes a datetime.timedelta and returns the total hours as a
    user-presentable float.
    """
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

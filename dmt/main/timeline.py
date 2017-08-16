from datetime import datetime

from django.template.defaultfilters import pluralize
from django.utils import timezone
from pytz import AmbiguousTimeError, NonExistentTimeError

from dmt.main.utils import interval_to_hours


class TimeLineItem(object):
    def __lt__(self, other):
        my_timestamp = self.timestamp()
        other_timestamp = other.timestamp()

        try:
            if timezone.is_naive(my_timestamp):
                my_timestamp = timezone.make_aware(my_timestamp)
        except (AmbiguousTimeError, NonExistentTimeError, AttributeError):
            # If an exception is raised, then it's not actually
            # a timestamp, it could be an int for testing purposes,
            # so let the comparison go through.
            pass  # nosec

        try:
            if timezone.is_naive(other_timestamp):
                other_timestamp = timezone.make_aware(other_timestamp)
        except (AmbiguousTimeError, NonExistentTimeError, AttributeError):
            pass  # nosec

        return my_timestamp < other_timestamp

    # methods to override

    def user(self):
        return None

    def project(self):
        return None

    def event_type(self):
        return None

    def timestamp(self):
        return None

    def title(self):
        return None

    def body(self):
        return None

    def label(self):
        return None

    def url(self):
        return None


class TimeLineEvent(TimeLineItem):
    def __init__(self, comment):
        self.c = comment
        self.event = comment.event
        self.u = self.c.user()

    def timestamp(self):
        return self.event.event_date_time

    def event_type(self):
        return "event"

    def title(self):
        return self.event.item.title

    def body(self):
        return self.c.comment

    def user(self):
        return self.u

    def url(self):
        return self.event.item.get_absolute_url()

    def project(self):
        return self.event.item.milestone.project


class TimeLineComment(TimeLineItem):
    def __init__(self, comment):
        self.c = comment

    def event_type(self):
        return "comment"

    def timestamp(self):
        return self.c.add_date_time

    def user(self):
        return self.c.user()

    def body(self):
        return self.c.comment

    def title(self):
        return self.c.item.title

    def label(self):
        return "COMMENT ADDED"

    def url(self):
        return self.c.item.get_absolute_url()

    def project(self):
        return self.c.item.milestone.project


class TimeLineActualTime(TimeLineItem):
    def __init__(self, actualtime):
        self.a = actualtime

    def timestamp(self):
        return self.a.completed

    def user(self):
        return self.a.user.userprofile

    def title(self):
        return self.a.item.title

    def body(self):
        hours = interval_to_hours(self.a.actual_time)
        return "{:.2f} hour{}".format(hours, pluralize(hours))

    def event_type(self):
        return "actual_time"

    def label(self):
        return "TIME LOGGED"

    def url(self):
        return self.a.item.get_absolute_url()

    def project(self):
        return self.a.item.milestone.project


class TimeLineStatus(TimeLineItem):
    def __init__(self, s):
        self.s = s

    def user(self):
        return self.s.author.userprofile

    def timestamp(self):
        return datetime.combine(self.s.added, datetime.min.time())

    def event_type(self):
        return "status_update"

    def title(self):
        return "status update"

    def body(self):
        return self.s.body

    def label(self):
        return "STATUS UPDATE"

    def project(self):
        return self.s.project


class TimeLinePost(TimeLineItem):
    def __init__(self, p):
        self.p = p

    def timestamp(self):
        return self.p.added

    def event_type(self):
        return "forum_post"

    def user(self):
        return self.p.user.userprofile

    def title(self):
        return self.p.subject

    def body(self):
        return self.p.body

    def label(self):
        return "FORUM POST"

    def url(self):
        return self.p.get_absolute_url()

    def project(self):
        return self.p.project


class TimeLineMilestone(TimeLineItem):
    def __init__(self, m):
        self.m = m

    def timestamp(self):
        return datetime.combine(self.m.target_date, datetime.min.time())

    def event_type(self):
        return "milestone"

    def title(self):
        return self.m.name

    def label(self):
        return "MILESTONE"

    def url(self):
        return self.m.get_absolute_url()

    def project(self):
        return self.m.project

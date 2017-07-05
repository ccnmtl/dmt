import pytz
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date


class PrevNextWeekMixin(object):
    """ A mixin for prev/next week params.

    This is meant to be attached to a View.
    """

    def __init__(self):
        self.calc_weeks(timezone.now())

    def get_params(self):
        """Update the interval based on request params."""
        date_str = self.request.GET.get('date', '')
        naive = parse_date(date_str)
        if date_str and naive:
            # Convert the date to a datetime
            naive = datetime.combine(naive, datetime.min.time())
            # Make the datetime tz-aware as documented here:
            # https://docs.djangoproject.com/en/1.8/topics/i18n/timezones/#usage
            aware = pytz.timezone(settings.TIME_ZONE).localize(naive)
        else:
            # There was no date param in the URL, so use now.
            aware = timezone.now()

        self.calc_weeks(aware)

    def get_context_data(self, *args, **kwargs):
        self.get_params()
        context = super(PrevNextWeekMixin, self).get_context_data(
            *args, **kwargs)
        return context

    def calc_weeks(self, now):
        self.now = now
        # Set week_start to the beginning of Monday.
        monday = now + timedelta(days=-self.now.weekday())
        self.week_start = pytz.timezone(settings.TIME_ZONE).localize(
            datetime.combine(monday, datetime.min.time()))

        # This week ends at 11:59:59 on Sunday night.
        self.week_end = self.week_start + timedelta(days=6,
                                                    hours=23,
                                                    minutes=59,
                                                    seconds=59)

        self.prev_week = self.week_start - timedelta(weeks=1)
        self.next_week = self.week_start + timedelta(weeks=1)

        fmt = '%Y-%m-%d'
        self.now_str = self.now.strftime(fmt)
        self.prev_week_str = self.prev_week.strftime(fmt)
        self.next_week_str = self.next_week.strftime(fmt)

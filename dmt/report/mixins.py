import pytz
from datetime import date, datetime, timedelta
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
            aware = pytz.timezone(settings.TIME_ZONE).localize(naive,
                                                               is_dst=None)
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
        self.week_start = datetime.combine(monday, datetime.min.time())

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


class RangeOffsetMixin(object):
    """ A mixin for range/offset day params.

    This is meant to be attached to a View. The mixin calculates dates
    using two keyword arguments in the GET request:

    - range: how many days in the past to look
    - offset: how many days in the past to skip

    So, for example, using the default values of 31 and 0, the view will
    report on all data that occured 31 days ago, up to present time (0 days
    ago). If you wanted to look at the data for the previous month a year
    ago, you could leave range at 31 and set offset to 365.
    """

    # 'range' is a built-in function in python, so to avoid confusion call
    # this range_days.
    range_days = 31
    offset_days = 0

    def calc_interval(self):
        # Calculate from the beginning of the first day in the range
        # to the end of the last day.
        naive_start = datetime.combine(date.today(), datetime.min.time()) - \
            timedelta(days=(self.range_days + self.offset_days))
        naive_end = datetime.combine(date.today(), datetime.max.time()) - \
            timedelta(days=(self.offset_days))

        # Convert to TZ-aware, based on the current timezone.
        aware_start = pytz.timezone(settings.TIME_ZONE).localize(
            naive_start, is_dst=None)
        aware_end = pytz.timezone(settings.TIME_ZONE).localize(
            naive_end, is_dst=None)

        self.interval_start = aware_start
        self.interval_end = aware_end

    def get_params(self):
        """Update the interval based on request params."""
        try:
            self.range_days = int(
                self.request.GET.get('range', self.range_days))
        except ValueError:
            # Just use the default if we can't parse the urlparam.
            self.range_days = 31

        try:
            self.offset_days = int(
                self.request.GET.get('offset', self.offset_days))
        except ValueError:
            self.offset_days = 0

        self.calc_interval()

    def get_context_data(self, *args, **kwargs):
        self.get_params()
        context = super(RangeOffsetMixin, self).get_context_data(
            *args, **kwargs)
        context.update({
            'range': self.range_days,
            'offset': self.offset_days,
            'interval_start': self.interval_start,
            'interval_end': self.interval_end,
        })
        return context

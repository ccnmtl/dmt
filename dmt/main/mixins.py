import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date


class DaterangeMixin(object):
    """A mixin for views that use daterange-datepicker pagination.

    This is meant to be attached to a View. The mixin calculates dates
    using two keyword arguments in the GET request:

    - interval_start
    - interval_end
    """

    interval_start = None
    interval_end = None
    delta = relativedelta(months=1)
    _today = None

    def today(self):
        if not self._today:
            self._today = timezone.localtime(timezone.now()).date()
        return self._today

    def calc_interval(self):
        # Calculate from the beginning of the first day in the range
        # to the end of the last day.
        naive_start = datetime.combine(
            self.interval_start, datetime.min.time())
        naive_end = datetime.combine(
            self.interval_end, datetime.max.time())

        # Convert to TZ-aware, based on the current timezone.
        aware_start = pytz.timezone(settings.TIME_ZONE).localize(
            naive_start, is_dst=None)
        aware_end = pytz.timezone(settings.TIME_ZONE).localize(
            naive_end, is_dst=None)

        self.interval_start = aware_start
        self.interval_end = aware_end

    def get_params(self):
        """Update the interval based on request params."""
        self.interval_start = self.request.GET.get('interval_start', None)
        self.interval_end = self.request.GET.get('interval_end', None)

        try:
            self.interval_start = parse_date(self.interval_start)
        except TypeError:
            pass
        try:
            self.interval_end = parse_date(self.interval_end)
        except TypeError:
            pass

        if not self.interval_start:
            self.interval_start = self.today() - self.delta
        if not self.interval_end:
            self.interval_end = self.today()

        self.calc_interval()

    def get_context_data(self, *args, **kwargs):
        self.get_params()
        context = super(DaterangeMixin, self).get_context_data(
            *args, **kwargs)
        context.update({
            'interval_start': self.interval_start,
            'interval_end': self.interval_end,
        })
        return context

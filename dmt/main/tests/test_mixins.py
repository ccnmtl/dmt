import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.test.client import RequestFactory
from dmt.main.mixins import DaterangeMixin


class DaterangeMixinTests(TestCase):
    def setUp(self):
        self.mixin = DaterangeMixin()
        self.rf = RequestFactory()

    def test_calc_prev_next_times(self):
        now = timezone.now()
        p, n = self.mixin.calc_prev_next_times(
            now - timedelta(days=7), now)
        delta = n - p
        self.assertEqual(
            delta.days, 7 * 3,
            'pagination bounds are 3 times the original delta apart')
        self.assertEqual(delta.seconds, 0)
        self.assertEqual(delta.microseconds, 0)

        p, n = self.mixin.calc_prev_next_times(
            now - timedelta(days=30), now)
        delta = n - p
        self.assertEqual(
            delta.days, 30 * 3,
            'pagination bounds are 3 times the original delta apart')

    def test_get_params(self):
        self.mixin.request = self.rf.get('/')
        today_date = parse_datetime('2016-01-02 00:00:00')
        naive_today = datetime.combine(
            parse_datetime('2016-01-02 00:00:00'), datetime.min.time())
        aware_today = pytz.timezone(settings.TIME_ZONE).localize(
            naive_today)
        naive_end = datetime.combine(aware_today, datetime.max.time())
        aware_end = pytz.timezone(settings.TIME_ZONE).localize(
            naive_end)

        self.mixin._today = today_date
        self.mixin.get_params()

        self.assertEqual(
            self.mixin.interval_start,
            aware_today - relativedelta(months=1))
        self.assertEqual(self.mixin.interval_end, aware_end)

        self.mixin.request = self.rf.get('/', {
            'interval_start': '2016-01-01',
            'interval_end': '2016-02-01',
        })
        self.mixin.get_params()

        naive_end = datetime.combine(
            parse_datetime('2016-02-01 00:00:00'),
            datetime.max.time())
        aware_end = pytz.timezone(settings.TIME_ZONE).localize(
            naive_end)
        naive_start = datetime.combine(
            aware_end - relativedelta(months=1), datetime.min.time())
        aware_start = pytz.timezone(settings.TIME_ZONE).localize(
            naive_start)
        self.assertEqual(self.mixin.interval_start, aware_start)
        self.assertEqual(self.mixin.interval_end, aware_end)

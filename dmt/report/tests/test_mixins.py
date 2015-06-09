import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.test import TestCase
from django.utils.dateparse import parse_datetime
from dmt.report.mixins import RangeOffsetMixin, PrevNextWeekMixin


class PrevNextWeekMixinTests(TestCase):
    def setUp(self):
        self.mixin = PrevNextWeekMixin()

    def test_calc_weeks(self):
        now = parse_datetime('2014-11-01 00:00:00')
        self.mixin.calc_weeks(now)
        self.assertEqual(
            self.mixin.week_start,
            parse_datetime('2014-10-27 00:00:00'))
        self.assertEqual(
            self.mixin.week_end,
            parse_datetime('2014-11-02 23:59:59'))
        self.assertEqual(
            self.mixin.prev_week,
            parse_datetime('2014-10-20 00:00:00'))
        self.assertEqual(
            self.mixin.next_week,
            parse_datetime('2014-11-03 00:00:00'))

        now = parse_datetime('2014-11-01 11:25:28')
        self.mixin.calc_weeks(now)
        self.assertEqual(
            self.mixin.week_start,
            parse_datetime('2014-10-27 00:00:00'),
            'It calculates the beginning of the week accurately')


class RangeOffsetMixinTests(TestCase):
    def setUp(self):
        self.mixin = RangeOffsetMixin()

    def test_calc_interval(self):
        self.mixin.calc_interval()
        naive_today = datetime.combine(date.today(), datetime.min.time())
        aware_today = pytz.timezone(settings.TIME_ZONE).localize(
            naive_today, is_dst=None)
        naive_end_of_today = datetime.combine(date.today(),
                                              datetime.max.time())
        aware_end_of_today = pytz.timezone(settings.TIME_ZONE).localize(
            naive_end_of_today, is_dst=None)

        self.assertEqual(self.mixin.interval_start,
                         aware_today - timedelta(days=31))
        self.assertEqual(self.mixin.interval_end, aware_end_of_today)

        self.mixin.offset_days = 3
        self.mixin.calc_interval()
        self.assertEqual(self.mixin.interval_start,
                         aware_today - timedelta(days=34))
        self.assertEqual(self.mixin.interval_end,
                         aware_end_of_today - timedelta(days=3))

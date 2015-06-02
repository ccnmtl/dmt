from datetime import date, timedelta
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


class RangeOffsetMixinTests(TestCase):
    def setUp(self):
        self.mixin = RangeOffsetMixin()

    def test_calc_interval(self):
        self.mixin.calc_interval()
        self.assertEqual(self.mixin.interval_start,
                         date.today() - timedelta(days=31))

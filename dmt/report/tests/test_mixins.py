from dateutil import parser
from datetime import date, timedelta
from django.test import TestCase
from dmt.report.mixins import RangeOffsetMixin, PrevNextWeekMixin


class PrevNextWeekMixinTests(TestCase):
    def setUp(self):
        self.mixin = PrevNextWeekMixin()

    def test_calc_weeks(self):
        now = parser.parse('Nov 1 2014 12pm')
        self.mixin.calc_weeks(now)
        self.assertEqual(
            self.mixin.week_start,
            parser.parse('Oct 27 2014 12pm'))
        self.assertEqual(
            self.mixin.week_end,
            parser.parse('Nov 2 2014 12pm'))
        self.assertEqual(
            self.mixin.prev_week,
            parser.parse('Oct 20 2014 12pm'))
        self.assertEqual(
            self.mixin.next_week,
            parser.parse('Nov 3 2014 12pm'))


class RangeOffsetMixinTests(TestCase):
    def setUp(self):
        self.mixin = RangeOffsetMixin()

    def test_calc_interval(self):
        self.mixin.calc_interval()
        self.assertEqual(self.mixin.interval_start,
                         date.today() - timedelta(days=31))

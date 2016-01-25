from django.test import TestCase
from django.utils.dateparse import parse_datetime
from dmt.report.mixins import PrevNextWeekMixin


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

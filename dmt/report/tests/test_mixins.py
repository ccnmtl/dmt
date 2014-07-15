from dateutil import parser
from django.test import TestCase
from ..mixins import PrevNextWeekMixin


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

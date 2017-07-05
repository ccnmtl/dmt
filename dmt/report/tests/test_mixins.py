import pytz
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from dmt.report.mixins import PrevNextWeekMixin


class PrevNextWeekMixinTests(TestCase):
    def setUp(self):
        self.mixin = PrevNextWeekMixin()

    def test_calc_weeks(self):
        tz = pytz.timezone(settings.TIME_ZONE)
        now = parse_datetime('2014-11-01 00:00:00').replace(tzinfo=tz)
        self.mixin.calc_weeks(now)
        self.assertEqual(
            timezone.make_naive(self.mixin.week_start),
            parse_datetime('2014-10-27 00:00:00'))
        self.assertEqual(
            timezone.make_naive(self.mixin.week_end),
            parse_datetime('2014-11-02 22:59:59'))
        self.assertEqual(
            timezone.make_naive(self.mixin.prev_week),
            parse_datetime('2014-10-20 00:00:00'))
        self.assertEqual(
            timezone.make_naive(self.mixin.next_week),
            parse_datetime('2014-11-02 23:00:00'))

        now = parse_datetime('2014-11-01 11:25:28').replace(tzinfo=tz)
        self.mixin.calc_weeks(now)
        self.assertEqual(
            timezone.make_naive(self.mixin.week_start),
            parse_datetime('2014-10-27 00:00:00'),
            'It calculates the beginning of the week accurately')

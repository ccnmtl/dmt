from datetime import datetime, timedelta
from django.test import TestCase
from django.conf import settings
import unittest
from ..models import StaffReportCalculator, WeeklySummaryReportCalculator


class StaffReportCalculatorTests(TestCase):
    def setUp(self):
        now = datetime.today()
        self.week_start = now + timedelta(days=-now.weekday())
        self.week_end = self.week_start + timedelta(days=6)

    def test_calc_no_groups(self):
        calc = StaffReportCalculator([])
        calc.calc(self.week_start, self.week_end)

    def test_calc_on_empty_db(self):
        calc = StaffReportCalculator(['programmers'])
        calc.calc(self.week_start, self.week_end)


class WeeklySummaryReportCalculatorTests(TestCase):
    def setUp(self):
        now = datetime.today()
        self.week_start = now + timedelta(days=-now.weekday())
        self.week_end = self.week_start + timedelta(days=6)

    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_calc_on_empty_db(self):
        calc = WeeklySummaryReportCalculator(['programmers'])
        calc.calc(self.week_start, self.week_end)

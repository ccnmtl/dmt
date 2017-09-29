from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from dmt.main.models import UserProfile
from dmt.main.tests.factories import UserProfileFactory
from dmt.report.calculators import (
    ActiveProjectsCalculator, StaffReportCalculator
)


class ActiveProjectsCalculatorTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.interval_start = now - timedelta(days=365)
        self.interval_end = self.interval_start + timedelta(days=365)

    def test_calc_on_empty_db(self):
        calc = ActiveProjectsCalculator()
        calc.calc(self.interval_start, self.interval_end)


class StaffReportCalculatorTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.week_start = now + timedelta(days=-now.weekday())
        self.week_end = self.week_start + timedelta(days=6)

    def test_calc(self):
        UserProfileFactory()
        UserProfileFactory()
        UserProfileFactory()
        calc = StaffReportCalculator(UserProfile.objects.all())
        calc.calc(self.week_start, self.week_end)

    def test_calc_on_empty_db(self):
        calc = StaffReportCalculator(UserProfile.objects.all())
        calc.calc(self.week_start, self.week_end)

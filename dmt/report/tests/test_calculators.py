import unittest
from datetime import timedelta
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from dmt.main.models import UserProfile
from dmt.main.tests.factories import (ProjectFactory, UserProfileFactory)
from dmt.report.calculators import (
    ActiveProjectsCalculator, StaffReportCalculator,
    TimeSpentByUserCalculator, TimeSpentByProjectCalculator,
    ProjectStatusCalculator,
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


@unittest.skipIf(
    settings.DATABASES['default']['ENGINE'] !=
    'django.db.backends.postgresql_psycopg2',
    "This test uses a raw PostgreSQL query")
class TimeSpentByUserCalculatorTest(TestCase):
    def test_calc(self):
        ProjectFactory()
        calc = TimeSpentByUserCalculator()
        calc.calc()

    def test_calc_on_empty_db(self):
        calc = TimeSpentByUserCalculator()
        calc.calc()


@unittest.skipIf(
    settings.DATABASES['default']['ENGINE'] !=
    'django.db.backends.postgresql_psycopg2',
    "This test uses a raw PostgreSQL query")
class TimeSpentByProjectCalculatorTest(TestCase):
    def test_calc(self):
        ProjectFactory()
        calc = TimeSpentByProjectCalculator()
        calc.calc()

    def test_calc_on_empty_db(self):
        calc = TimeSpentByProjectCalculator()
        calc.calc()


@unittest.skipIf(
    settings.DATABASES['default']['ENGINE'] !=
    'django.db.backends.postgresql_psycopg2',
    "This test uses a raw PostgreSQL query")
class ProjectStatusCalculatorTest(TestCase):
    def test_calc(self):
        ProjectFactory()
        UserProfileFactory()
        UserProfileFactory()
        UserProfileFactory()
        calc = ProjectStatusCalculator()
        calc.calc()

    def test_calc_on_empty_db(self):
        calc = ProjectStatusCalculator()
        calc.calc()

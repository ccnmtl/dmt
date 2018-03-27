from datetime import timedelta
import unittest

from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from dmt.main.models import UserProfile
from dmt.main.tests.factories import (
    ProjectFactory, UserProfileFactory, ItemFactory)
from dmt.report.calculators import (
    ActiveProjectsCalculator, StaffReportCalculator,
    TimeSpentByUserCalculator, TimeSpentByProjectCalculator,
    ProjectStatusCalculator, StaffCapacityCalculator
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


class StaffCapacityCalculatorTest(TestCase):

    def test_capacity_skip_weekend(self):
        UserProfileFactory()
        start = parse_datetime('2018-05-14 00:00:00-04:00')
        end = parse_datetime('2018-05-25 23:59:59.999999-04:00')

        calc = StaffCapacityCalculator(
            UserProfile.objects.all(), start, end)
        self.assertEquals(calc.days(), 10)
        self.assertEquals(calc.capacity_for_range(), 60)

    def test_capacity_skip_holiday(self):
        UserProfileFactory()
        start = parse_datetime('2018-05-28 00:00:00-04:00')
        end = parse_datetime('2018-06-01 23:59:59.999999-04:00')

        calc = StaffCapacityCalculator(
            UserProfile.objects.all(), start, end)
        self.assertEquals(calc.days(), 4)
        self.assertEquals(calc.capacity_for_range(), 24)

    def test_calc(self):
        start = parse_datetime('2017-05-15 00:00:00-04:00')
        end = parse_datetime('2017-05-26 23:59:59.999999-04:00')
        target = parse_datetime('2017-05-16 00:00:00-04:00')

        profile = UserProfileFactory()
        ItemFactory(assigned_user=profile.user,
                    estimated_time=timedelta(hours=5),
                    target_date=target)
        ItemFactory(assigned_user=profile.user,
                    estimated_time=timedelta(hours=1))

        calc = StaffCapacityCalculator(
            UserProfile.objects.filter(user__id=profile.user.id),
            start, end)
        self.assertEquals(calc.days(), 10)
        self.assertEquals(calc.capacity_for_range(), 60)

        data = calc.calc()
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]['user'], profile)
        self.assertEquals(data[0]['booked'], 5)
        self.assertEquals(data[0]['percent_booked'], '8.3')
        self.assertEquals(data[0]['available'], 55)
        self.assertEquals(data[0]['percent_available'], '91.7')

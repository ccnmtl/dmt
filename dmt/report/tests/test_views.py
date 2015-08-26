from datetime import timedelta
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from dmt.main.models import InGroup
from dmt.main.tests.factories import (
    ActualTimeFactory, ItemFactory, MilestoneFactory, UserProfileFactory
)
from dmt.main.tests.support.mixins import LoggedInTestMixin
import unittest


class ActiveProjectTests(LoggedInTestMixin, TestCase):
    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_active_project_view(self):
        r = self.client.get(reverse('active_projects_report'))
        self.assertEqual(r.status_code, 200)


class ActiveProjectExportTests(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(ActiveProjectExportTests, self).setUp()
        completed = timezone.now() - timedelta(days=3)
        ActualTimeFactory(completed=completed)

    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_active_project_export_csv_view(self):
        r = self.client.get(
            reverse('active_projects_report_export') +
            '?format=csv&range=31&offset=0')
        self.assertEqual(r.status_code, 200)

        r_offset = self.client.get(
            reverse('active_projects_report_export') +
            '?format=csv&range=31&offset=100')
        self.assertEqual(r_offset.status_code, 200)
        self.assertNotEqual(r.content, r_offset.content)

    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_active_project_export_excel_view(self):
        r = self.client.get(
            reverse('active_projects_report_export') +
            '?format=xlsx&range=31&offset=0')
        self.assertEqual(r.status_code, 200)

        r_offset = self.client.get(
            reverse('active_projects_report_export') +
            '?format=xlsx&range=31&offset=100')
        self.assertEqual(r_offset.status_code, 200)
        self.assertNotEqual(r.content, r_offset.content)


class UserWeeklyTest(LoggedInTestMixin, TestCase):
    def test_user_weekly(self):
        r = self.client.get("/report/user/testuser/weekly/")
        self.assertEqual(r.status_code, 200)

    def test_user_weekly_date_specified(self):
        r = self.client.get("/report/user/testuser/weekly/?date=2012-12-16")
        self.assertEqual(r.status_code, 200)

    def test_user_weekly_bogus_date(self):
        r = self.client.get("/report/user/testuser/weekly/?date=zijf3jf093j")
        self.assertEqual(r.status_code, 200)

    def test_user_weekly_empty_date(self):
        r = self.client.get("/report/user/testuser/weekly/?date=")
        self.assertEqual(r.status_code, 200)


class UserYearlyTest(LoggedInTestMixin, TestCase):
    def test_yearly_review_redirect(self):
        r = self.client.get("/report/yearly_review/")
        self.assertEqual(r.status_code, 302)

    def test_user_yearly(self):
        r = self.client.get("/report/user/testuser/yearly/")
        self.assertEqual(r.status_code, 200)


class StaffReportTest(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(StaffReportTest, self).setUp()
        self.pg = UserProfileFactory(username='grp_programmers',
                                     fullname='programmers (group)')
        InGroup.objects.create(grp=self.pg, username=self.pu)

    def test_staff_report_date_specified(self):
        r = self.client.get("/report/staff/?date=2012-12-16")
        self.assertEqual(r.status_code, 200)

    def test_staff_report(self):
        r = self.client.get("/report/staff/")
        self.assertEqual(r.status_code, 200)

    def test_staff_report_previous(self):
        r = self.client.get("/report/staff/previous/")
        self.assertEqual(r.status_code, 302)


class StaffReportExportTests(LoggedInTestMixin, TestCase):
    def test_active_project_export_csv_view(self):
        r = self.client.get(
            reverse('staff_report_export') +
            '?format=csv&range=7&offset=0')
        self.assertEqual(r.status_code, 200)

    def test_active_project_export_excel_view(self):
        r = self.client.get(
            reverse('staff_report_export') +
            '?format=xlsx&range=7&offset=0')
        self.assertEqual(r.status_code, 200)


class ResolvedItemsTest(LoggedInTestMixin, TestCase):
    def test_view(self):
        i = ItemFactory(status='RESOLVED')
        r = self.client.get(reverse('resolved_items_report'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(i.title in r.content)


class WeeklySummaryTests(LoggedInTestMixin, TestCase):
    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_weekly_summary_view(self):
        r = self.client.get(reverse('weekly_summary_report'))
        self.assertEqual(r.status_code, 200)


class WeeklySummaryExportTests(LoggedInTestMixin, TestCase):
    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_weekly_summary_export_csv_view(self):
        r = self.client.get(reverse('weekly_summary_report_export') +
                            '?format=csv')
        self.assertEqual(r.status_code, 200)

    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_weekly_summar_export_excel_view(self):
        r = self.client.get(reverse('weekly_summary_report_export') +
                            '?format=xlsx')
        self.assertEqual(r.status_code, 200)


class PassedMilestonesViewTests(LoggedInTestMixin, TestCase):
    def test_report(self):
        m = MilestoneFactory(target_date='2000-01-01', status='OPEN')
        r = self.client.get(reverse('passed_milestones_report'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(m.name in r.content)


class ProjectHoursViewTests(LoggedInTestMixin, TestCase):
    def test_report(self):
        i = ItemFactory()
        p = i.milestone.project
        r = self.client.get(
            reverse('project-hours-report', args=[p.pid]) + "?format=csv")
        self.assertEqual(r.status_code, 200)

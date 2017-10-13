from datetime import timedelta
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from freezegun import freeze_time
from dmt.main.tests.factories import (
    ActualTimeFactory, ItemFactory, MilestoneFactory, UserProfileFactory
)
from dmt.main.tests.support.mixins import LoggedInTestMixin


class ActiveProjectTests(LoggedInTestMixin, TestCase):
    def test_active_project_view(self):
        r = self.client.get(reverse('active_projects_report'))
        self.assertEqual(r.status_code, 200)


class ActiveProjectExportTests(LoggedInTestMixin, TestCase):
    def setUp(self):
        self.freezer = freeze_time("2016-02-01 00:00:00")
        self.freezer.start()
        super(ActiveProjectExportTests, self).setUp()
        completed = timezone.now() - timedelta(days=35)
        ActualTimeFactory(completed=completed)

    def tearDown(self):
        self.freezer.stop()

    def test_active_project_export_csv_view(self):
        r = self.client.get(
            reverse('active_projects_report_export'), {
                'format': 'csv',
                'interval_start': '2016-01-01',
                'interval_end': '2016-02-01',
            })
        self.assertEqual(r.status_code, 200)

        r_offset = self.client.get(
            reverse('active_projects_report_export'), {
                'format': 'csv',
                'interval_start': '2015-12-01',
                'interval_end': '2016-02-01',
            })
        self.assertEqual(r_offset.status_code, 200)
        self.assertNotEqual(r.content, r_offset.content)

    def test_active_project_export_excel_view(self):
        r = self.client.get(
            reverse('active_projects_report_export'), {
                'format': 'xlsx',
                'interval_start': '2016-01-01',
                'interval_end': '2016-02-01',
            })
        self.assertEqual(r.status_code, 200)

        r_offset = self.client.get(
            reverse('active_projects_report_export'), {
                'format': 'xlsx',
                'interval_start': '2015-12-01',
                'interval_end': '2016-02-01',
            })
        self.assertEqual(r_offset.status_code, 200)
        self.assertNotEqual(r.content, r_offset.content)


class UserWeeklyTest(LoggedInTestMixin, TestCase):
    def test_user_weekly(self):
        r = self.client.get(
            reverse('user_weekly_report',
                    args=(self.u.userprofile.username,)))
        self.assertEqual(r.status_code, 200)

    def test_user_weekly_date_specified(self):
        r = self.client.get(
            reverse('user_weekly_report',
                    args=(self.u.userprofile.username,)) + '?date=2012-12-16')
        self.assertEqual(r.status_code, 200)

    def test_user_weekly_bogus_date(self):
        r = self.client.get(
            reverse('user_weekly_report',
                    args=(self.u.userprofile.username,)) + '?date=zijf3jf093j')
        self.assertEqual(r.status_code, 200)


class UserYearlyTest(LoggedInTestMixin, TestCase):
    def test_yearly_review_redirect(self):
        r = self.client.get("/report/yearly_review/")
        self.assertEqual(r.status_code, 302)

    def test_user_yearly(self):
        r = self.client.get(
            reverse('user_yearly_report',
                    args=(self.u.userprofile.username,)))
        self.assertEqual(r.status_code, 200)


class StaffReportTest(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(StaffReportTest, self).setUp()
        UserProfileFactory()

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
            reverse('staff_report_export'), {
                'format': 'csv',
                'interval_start': '2016-01-01',
                'interval_end': '2016-02-01',
            })
        self.assertEqual(r.status_code, 200)

    def test_active_project_export_excel_view(self):
        r = self.client.get(
            reverse('staff_report_export'), {
                'format': 'xlsx',
                'interval_start': '2016-01-01',
                'interval_end': '2016-02-01',
            })
        self.assertEqual(r.status_code, 200)


class ResolvedItemsTest(LoggedInTestMixin, TestCase):
    def test_view(self):
        i = ItemFactory(status='RESOLVED')
        r = self.client.get(reverse('resolved_items_report'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, i.title)


class InprogressItemsViewTest(LoggedInTestMixin, TestCase):
    def test_view(self):
        i = ItemFactory(status='INPROGRESS')
        r = self.client.get(reverse('inprogress_items_report'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, i.title)


class PassedMilestonesViewTests(LoggedInTestMixin, TestCase):
    def test_report(self):
        m = MilestoneFactory(target_date='2000-01-01', status='OPEN')
        r = self.client.get(reverse('passed_milestones_report'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(m.name in r.content)


class ProjectHoursViewTests(LoggedInTestMixin, TestCase):
    def test_get(self):
        i = ItemFactory()
        p = i.milestone.project
        r = self.client.get(
            reverse('project-hours-report', args=[p.pid]) + '?format=csv')
        self.assertEqual(r.status_code, 200)

    def test_get_with_interval_params(self):
        i = ItemFactory()
        p = i.milestone.project
        r = self.client.get(
            reverse('project-hours-report', args=[p.pid]), {
                'format': 'csv',
                'interval_start': '2015-12-01',
                'interval_end': '2016-02-01',
            })
        self.assertEqual(r.status_code, 200)

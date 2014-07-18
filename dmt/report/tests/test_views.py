from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from dmt.main.models import User as PMTUser
from dmt.claim.models import Claim
from dmt.main.models import InGroup
from dmt.main.tests.factories import ItemFactory


class ActiveProjectTests(TestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.client.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username='testuser',
                                         fullname='test user')
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_active_project_view(self):
        r = self.client.get(reverse('active_projects_report'))
        self.assertEqual(r.status_code, 200)


class UserWeeklyTest(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username='testuser',
                                         fullname='test user')
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_user_weekly(self):
        r = self.c.get("/report/user/testuser/weekly/")
        self.assertEqual(r.status_code, 200)

    def test_user_weekly_date_specified(self):
        r = self.c.get("/report/user/testuser/weekly/?date=2012-12-16")
        self.assertEqual(r.status_code, 200)


class UserYearlyTest(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username='testuser',
                                         fullname='test user')
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_yearly_review_redirect(self):
        r = self.c.get("/report/yearly_review/")
        self.assertEqual(r.status_code, 302)

    def test_user_yearly(self):
        r = self.c.get("/report/user/testuser/yearly/")
        self.assertEqual(r.status_code, 200)


class StaffReportTest(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username='testuser',
                                         fullname='test user')
        self.pg = PMTUser.objects.create(username='grp_programmers',
                                         fullname='programmers (group)')
        InGroup.objects.create(grp=self.pg, username=self.pu)
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_staff_report_date_specified(self):
        r = self.c.get("/report/staff/?date=2012-12-16")
        self.assertEqual(r.status_code, 200)

    def test_staff_report(self):
        r = self.c.get("/report/staff/")
        self.assertEqual(r.status_code, 200)

    def test_staff_report_previous(self):
        r = self.c.get("/report/staff/previous/")
        self.assertEqual(r.status_code, 302)


class ResolvedItemsTest(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username='testuser',
                                         fullname='test user')
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_view(self):
        i = ItemFactory(status='RESOLVED')
        r = self.c.get(reverse('resolved_items_report'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(i.title in r.content)


class WeeklySummaryTests(TestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.client.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username='testuser',
                                         fullname='test user')
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_weekly_summary_view(self):
        r = self.client.get(reverse('weekly_summary_report'))
        self.assertEqual(r.status_code, 200)

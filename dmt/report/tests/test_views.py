from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from dmt.main.models import User as PMTUser
from dmt.claim.models import Claim
from dmt.main.models import InGroup


class UserWeeklyTest(TestCase):
    def setUp(self):
        self.c = Client()
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
        self.c = Client()
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
        self.c = Client()
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

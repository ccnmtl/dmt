from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from dmt.main.models import User as PMTUser


class UserWeeklyTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username='testuser',
                                         fullname='test user')

    def test_user_weekly(self):
        r = self.c.get("/report/user/testuser/weekly/")
        self.assertEqual(r.status_code, 200)

    def test_user_weekly_date_specified(self):
        r = self.c.get("/report/user/testuser/weekly/?date=2012-12-16")
        self.assertEqual(r.status_code, 200)

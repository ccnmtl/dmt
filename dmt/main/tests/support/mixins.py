from django.contrib.auth.models import User
from django.test import TestCase
from dmt.claim.models import Claim
from dmt.main.models import User as PMTUser


class LoggedInTestMixin(TestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.client.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username='testuser',
                                         fullname='test user')
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

from casper.tests import CasperTestCase
from django.contrib.auth.models import User
import os.path

from dmt.claim.models import Claim, PMTUser


class CasperIntegrationTestsAnonUser(CasperTestCase):
    def test_integration_tests_anon_user(self):
        self.assertTrue(self.casper(
            os.path.join(os.path.dirname(__file__),
                         'js/integration_tests_anon_user.js')))


class CasperIntegrationTestsLoggedIn(CasperTestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.client.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_integration_tests_logged_in(self):
        self.assertTrue(self.casper(
            os.path.join(os.path.dirname(__file__),
                         'js/integration_tests_logged_in.js')))

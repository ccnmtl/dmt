from django.test import TestCase
from dmt.claim.models import Claim, DjangoUser, PMTUser
from dmt.claim.models import all_unclaimed_pmt_users


class ClaimTest(TestCase):
    def test_unicode(self):
        du = DjangoUser.objects.create(username="testdjangouser")
        pu = PMTUser.objects.create(username="testpmtuser",
                                    email="testemail@columbia.edu")
        claim = Claim.objects.create(django_user=du, pmt_user=pu)
        self.assertEqual(str(claim), "testdjangouser has claimed testpmtuser")


class QueryTest(TestCase):
    def test_all_unclaimed_pmt_users_empty(self):
        self.assertEqual(list(all_unclaimed_pmt_users()), [])

    def test_all_unclaimed_pmt_users_populated(self):
        pu = PMTUser.objects.create(username="testpmtuser",
                                    email="testemail@columbia.edu",
                                    status='active')
        self.assertTrue(
            pu.username in [
                p.username for p in list(all_unclaimed_pmt_users())])

    def test_all_unclaimed_pmt_users_claimed(self):
        pu = PMTUser.objects.create(username="testpmtuser",
                                    email="testemail@columbia.edu",
                                    status='active')
        du = DjangoUser.objects.create(username="testdjangouser")
        Claim.objects.create(django_user=du, pmt_user=pu)
        self.assertFalse(
            pu.username in [
                p.username for p in list(all_unclaimed_pmt_users())])

    def test_all_unclaimed_pmt_users_group(self):
        pu = PMTUser.objects.create(username="grp_testpmtuser",
                                    email="testemail@columbia.edu",
                                    status='active')
        self.assertFalse(
            pu.username in [
                p.username for p in list(all_unclaimed_pmt_users())])

    def test_all_unclaimed_pmt_users_inactive(self):
        pu = PMTUser.objects.create(username="testpmtuser",
                                    email="testemail@columbia.edu",
                                    status='inactive')
        self.assertFalse(
            pu.username in [
                p.username for p in list(all_unclaimed_pmt_users())])

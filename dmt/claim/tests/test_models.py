from django.test import TestCase
from dmt.claim.models import Claim, DjangoUser, PMTUser


class ClaimTest(TestCase):
    def test_unicode(self):
        du = DjangoUser.objects.create(username="testdjangouser")
        pu = PMTUser.objects.create(username="testpmtuser",
                                    email="testemail@columbia.edu")
        claim = Claim.objects.create(django_user=du, pmt_user=pu)
        self.assertEqual(str(claim), "testdjangouser has claimed testpmtuser")

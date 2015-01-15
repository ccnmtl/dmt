from django.test import TestCase
from dmt.claim.models import Claim, DjangoUser
from dmt.claim.models import all_unclaimed_pmt_users


class ClaimTest(TestCase):
    def test_unicode(self):
        du = DjangoUser.objects.create(username="testdjangouser")
        claim = Claim.objects.get(django_user=du)
        self.assertEqual(str(claim),
                         "testdjangouser has claimed testdjangouser")

    def test_from_django_user(self):
        du = DjangoUser.objects.create(username="testdjangouser")
        claim = Claim.objects.get(django_user=du)
        self.assertEqual(claim.id, Claim.from_django_user(du).id)

    def test_from_pmt_user(self):
        du = DjangoUser.objects.create(username="testdjangouser")
        claim = Claim.objects.get(pmt_user=du.userprofile)
        self.assertEqual(claim.id, Claim.from_pmt_user(du.userprofile).id)


class QueryTest(TestCase):
    def test_all_unclaimed_pmt_users_empty(self):
        self.assertEqual(list(all_unclaimed_pmt_users()), [])

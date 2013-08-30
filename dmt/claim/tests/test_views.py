from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from dmt.claim.models import Claim, PMTUser


class IndexViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")

    def test_index_get_claimed(self):
        pu = PMTUser.objects.create(username="testpmtuser",
                                    email="testemail@columbia.edu",
                                    status="active")
        Claim.objects.create(django_user=self.u, pmt_user=pu)
        response = self.c.get("/claim/")
        self.assertEquals(response.status_code, 200)
        self.assertTrue("You have claimed the" in response.content)

    def test_index_get_unclaimed(self):
        PMTUser.objects.create(username="testpmtuser",
                               fullname="something that won't match",
                               email="testemail@columbia.edu",
                               status="active")
        response = self.c.get("/claim/")
        self.assertEquals(response.status_code, 200)
        self.assertFalse("You have claimed the" in response.content)
        self.assertTrue("<select " in response.content)
        self.assertTrue("value=\"testpmtuser\"" in response.content)
        self.assertFalse("selected=" in response.content)

    def test_index_get_unclaimed_with_likely(self):
        PMTUser.objects.create(username="testuser",
                               email="testemail@columbia.edu",
                               status='active')
        response = self.c.get("/claim/")
        self.assertEquals(response.status_code, 200)
        self.assertFalse("You have claimed the" in response.content)
        self.assertTrue("<select " in response.content)
        self.assertTrue("value=\"testuser\"" in response.content)
        self.assertTrue("selected=" in response.content)

    def test_index_post(self):
        PMTUser.objects.create(username="testpmtuser",
                               email="testemail@columbia.edu",
                               status="active")
        response = self.c.get("/claim/")
        self.assertEquals(response.status_code, 200)
        self.assertFalse("You have claimed the" in response.content)
        self.assertTrue("<select " in response.content)
        self.assertTrue("value=\"testpmtuser\"" in response.content)
        self.assertEqual(Claim.objects.count(), 0)

        response = self.c.post("/claim/", dict(user="testpmtuser"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Claim.objects.count(), 1)

        response = self.c.get("/claim/")
        self.assertEquals(response.status_code, 200)
        self.assertTrue("You have claimed the" in response.content)

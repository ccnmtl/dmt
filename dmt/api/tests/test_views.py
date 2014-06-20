from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from dmt.claim.models import Claim, PMTUser
from dmt.main.models import Notify
from dmt.main.tests.factories import MilestoneFactory, ClientFactory
from dmt.main.tests.factories import ItemFactory, NotifyFactory

from ..serializers import ItemSerializer


class AddTrackerViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        pu = PMTUser.objects.create(username="testpmtuser",
                                    email="testemail@columbia.edu",
                                    status="active")
        Claim.objects.create(django_user=self.u, pmt_user=pu)
        m = MilestoneFactory()
        self.project = m.project

    def test_post_without_required_fields(self):
        r = self.c.post(
            "/api/1.0/trackers/add/",
            dict())
        self.assertEqual(r.status_code, 200)

    def test_post(self):
        r = self.c.post(
            "/api/1.0/trackers/add/",
            dict(
                pid=self.project.pid,
                task="test",
                time="1 hour",
            ))
        self.assertEqual(r.status_code, 200)

    def test_post_with_nonexistant_client(self):
        r = self.c.post(
            "/api/1.0/trackers/add/",
            dict(
                pid=self.project.pid,
                task="test",
                time="1 hour",
                client="foo",
            ))
        self.assertEqual(r.status_code, 200)

    def test_post_with_client(self):
        self.client = ClientFactory()
        r = self.c.post(
            "/api/1.0/trackers/add/",
            dict(
                pid=self.project.pid,
                task="test",
                time="1 hour",
                client="testclient",
            ))
        self.assertEqual(r.status_code, 200)

    def test_with_duplicate_clients(self):
        self.client = ClientFactory()
        self.client2 = ClientFactory()
        self.client2.email = self.client.email
        self.client2.save()
        r = self.c.post(
            "/api/1.0/trackers/add/",
            dict(
                pid=self.project.pid,
                task="test",
                time="1 hour",
                client="testclient",
            ))
        self.assertEqual(r.status_code, 200)


class ItemHoursViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        pu = PMTUser.objects.create(username="testpmtuser",
                                    email="testemail@columbia.edu",
                                    status="active")
        Claim.objects.create(django_user=self.u, pmt_user=pu)
        self.item = ItemFactory()

    def test_post(self):
        r = self.c.post(
            "/api/1.0/items/%d/hours/" % self.item.iid,
            dict(
                time="1 hour",
            ))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "ok")


class GitUpdateViewTest(TestCase):
    def setUp(self):
        self.c = Client()

    def test_post_fixed(self):
        i = ItemFactory()
        i.save()
        r = self.c.post(
            "/api/1.0/git/",
            dict(status='FIXED',
                 iid=i.iid,
                 email=i.assigned_to.email,
                 comment="a comment")
            )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "ok")

    def test_post_fixed_with_resolve_time(self):
        i = ItemFactory()
        i.save()
        r = self.c.post(
            "/api/1.0/git/",
            dict(status='FIXED',
                 iid=i.iid,
                 email=i.assigned_to.email,
                 resolve_time='1 hour',
                 comment="a comment")
            )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "ok")

    def test_post_comment(self):
        i = ItemFactory()
        i.save()
        r = self.c.post(
            "/api/1.0/git/",
            dict(iid=i.iid,
                 email=i.assigned_to.email,
                 comment="a comment")
            )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "ok")


class ItemTests(APITestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.item = ItemFactory()
        self.client.force_authenticate(user=self.u)

    def test_get(self):
        r = self.client.get(
            reverse('item-detail', kwargs={'pk':self.item.iid}))
        self.assertEqual(r.status_code, 200)

        # Loop through the simple attributes of the item
        for attr in ItemSerializer.Meta.fields:
            if (hasattr(self.item.__dict__, attr)):
                self.assertEqual(r.data[attr], self.item.__dict__[attr])

        # Verify accuracy of relationships
        self.assertIn(self.item.owner.username.lower(),
                      r.data["owner"].lower())
        self.assertIn(self.item.assigned_to.username.lower(),
                      r.data["assigned_to"].lower())

    def test_get_with_notification(self):
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

        self.notification = NotifyFactory(item=self.item, username=self.pu)

        r = self.client.get(
            reverse('item-detail', kwargs={'pk':self.item.iid}))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['iid'], self.item.iid)

        usernames = [n.lower() for n in r.data['notifies']]
        self.assertIn(self.pu.username.lower(), usernames)


class NotifyTests(APITestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                    email="testemail@columbia.edu",
                                    status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)
        self.item = ItemFactory()
        self.n = NotifyFactory(item=self.item, username=self.pu)
        self.url = reverse("notify", kwargs={'pk':self.n.item.iid})

    def test_delete(self):
        self.client.login(username=self.u.username, password="test")
        r = self.client.delete(self.url)
        self.assertEqual(r.status_code, 204)

        user = Claim.objects.get(django_user=self.u).pmt_user
        notify = Notify.objects.filter(item=self.item, username=user)
        self.assertEqual(len(notify), 0)

    def test_delete_not_logged_in(self):
        r = self.client.delete(self.url)
        self.assertEqual(r.status_code, 403)

    def test_get(self):
        self.client.login(username=self.u.username, password="test")
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)

    def test_get_different_user(self):
        user2 = User.objects.create(username="testuser2")
        user2.set_password("test")
        user2.save()
        self.client.login(username=user2.username, password="test")

        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 404)

    def test_get_not_logged_in(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 404)

    def test_post(self):
        self.client.login(username=self.u.username, password="test")
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 201)

        user = Claim.objects.get(django_user=self.u).pmt_user
        notify = Notify.objects.get(item=self.item, username=user)
        self.assertIsInstance(notify, Notify)

    def test_post_not_logged_in(self):
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 403)

    def test_put(self):
        self.client.login(username=self.u.username, password="test")
        r = self.client.put(self.url)
        self.assertEqual(r.status_code, 201)

        user = Claim.objects.get(django_user=self.u).pmt_user
        notify = Notify.objects.get(item=self.item, username=user)
        self.assertIsInstance(notify, Notify)

    def test_put_not_logged_in(self):
        r = self.client.put(self.url)
        self.assertEqual(r.status_code, 403)


class ProjectsTest(APITestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.client.force_authenticate(user=self.u)

    def test_get(self):
        r = self.client.get(reverse("project-list"))
        self.assertEqual(r.status_code, 200)

    def test_search(self):
        url = reverse("project-list")
        data = {'search': 'test'}
        r = self.client.get(url, data)
        self.assertEqual(r.status_code, 200)

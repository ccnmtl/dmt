import json

from datetime import datetime, timedelta

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from dmt.main.models import ActualTime, Item, Notify
from dmt.main.tests.factories import (
    ClientFactory, MilestoneFactory, ProjectFactory, UserProfileFactory
)
from dmt.main.tests.factories import ItemFactory, NotifyFactory

from dmt.api.serializers import ItemSerializer


class AddTrackerViewTest(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.milestone = MilestoneFactory()
        self.project = self.milestone.project
        self.url = reverse('add-tracker')

    def test_post_without_required_fields(self):
        r = self.c.post(
            self.url,
            dict())
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_with_empty_fields(self):
        r = self.c.post(
            self.url,
            dict(pid='', task=''))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post(self):
        r = self.c.post(
            self.url,
            dict(
                pid=self.project.pid,
                task="test",
                time="1 hour",
            ))
        self.assertEqual(r.status_code, 200)

    def test_post_backdated_last(self):
        r = self.c.post(
            self.url,
            dict(
                pid=self.project.pid,
                task="test backdated last",
                time="1 hour",
                completed="last",
            ))
        self.assertEqual(r.status_code, 200)
        content = json.loads(r.content)
        self.assertEqual(content['duration'], 3600)
        self.assertEqual(content['simpleduration'], '1h')

        # Assert that the created time is accurate
        item = Item.objects.filter(
            milestone=self.milestone,
            title="test backdated last"
        ).first()
        actual_time = ActualTime.objects.filter(item=item).first()
        expected_time = datetime.utcnow() - timedelta(days=7)
        self.assertEqual(actual_time.completed.day, expected_time.day)
        self.assertEqual(actual_time.completed.month, expected_time.month)
        self.assertEqual(actual_time.completed.year, expected_time.year)

    def test_post_backdated_before_last(self):
        r = self.c.post(
            self.url,
            dict(
                pid=self.project.pid,
                task="test",
                time="1 hour",
                completed="before_last",
            ))
        self.assertEqual(r.status_code, 200)

        item = Item.objects.filter(milestone=self.milestone).first()
        actual_time = ActualTime.objects.filter(item=item).first()
        expected_time = datetime.utcnow() - timedelta(days=14)
        self.assertEqual(actual_time.completed.day, expected_time.day)
        self.assertEqual(actual_time.completed.month, expected_time.month)
        self.assertEqual(actual_time.completed.year, expected_time.year)

    def test_post_with_nonexistant_client(self):
        r = self.c.post(
            self.url,
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
            self.url,
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
            self.url,
            dict(
                pid=self.project.pid,
                task="test",
                time="1 hour",
                client="testclient",
            ))
        self.assertEqual(r.status_code, 200)


class ItemHoursViewTest(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.item = ItemFactory()

    def test_post(self):
        r = self.c.post(
            reverse('item-hours', kwargs={'pk': self.item.iid}),
            dict(
                time="1 hour",
            ))
        self.assertEqual(r.status_code, 201)

        content = json.loads(r.content)
        self.assertEqual(content['duration'], 3600)
        self.assertEqual(content['simpleduration'], '1h')

        r = self.c.post(
            reverse('item-hours', kwargs={'pk': self.item.iid}),
            dict(
                time="2h",
            ))
        self.assertEqual(r.status_code, 201)

        content = json.loads(r.content)
        self.assertEqual(content['duration'], 3600 * 2)
        self.assertEqual(content['simpleduration'], '2h')

    def test_post_empty_string(self):
        r = self.c.post(
            reverse('item-hours', kwargs={'pk': self.item.iid}),
            dict(
                time='',
            ))
        self.assertEqual(r.status_code, 201)

        content = json.loads(r.content)
        self.assertEqual(content['duration'], 0)

    def test_post_duration_no_units(self):
        r = self.c.post(
            reverse('item-hours', kwargs={'pk': self.item.iid}),
            dict(
                time='4',
            ))
        self.assertEqual(r.status_code, 201)

        content = json.loads(r.content)
        self.assertEqual(content['duration'], 3600 * 4)
        self.assertEqual(content['simpleduration'], '4h')

    def test_post_duration_no_units_with_whitespace(self):
        r = self.c.post(
            reverse('item-hours', kwargs={'pk': self.item.iid}),
            dict(
                time='4 ',
            ))
        self.assertEqual(r.status_code, 201)

        content = json.loads(r.content)
        self.assertEqual(content['duration'], 3600 * 4)
        self.assertEqual(content['simpleduration'], '4h')

        r = self.c.post(
            reverse('item-hours', kwargs={'pk': self.item.iid}),
            dict(
                time='  4',
            ))
        self.assertEqual(r.status_code, 201)

        content = json.loads(r.content)
        self.assertEqual(content['duration'], 3600 * 4)
        self.assertEqual(content['simpleduration'], '4h')

    def test_post_duration_invalid(self):
        r = self.c.post(
            reverse('item-hours', kwargs={'pk': self.item.iid}),
            dict(
                time='4 j',
            ))
        self.assertEqual(r.status_code, 201)

        content = json.loads(r.content)
        self.assertEqual(content['duration'], 0)

        r = self.c.post(
            reverse('item-hours', kwargs={'pk': self.item.iid}),
            dict(
                time='1h 30m invalid',
            ))
        self.assertEqual(r.status_code, 201)

        content = json.loads(r.content)
        self.assertEqual(content['duration'], 0)


class GitUpdateViewTest(TestCase):
    def setUp(self):
        self.c = self.client
        self.url = reverse('git-update')

    def test_post_fixed(self):
        i = ItemFactory()
        i.save()
        r = self.c.post(
            self.url,
            dict(status='FIXED',
                 iid=i.iid,
                 email=i.assigned_user.userprofile.email,
                 comment="a comment")
            )
        self.assertEqual(r.status_code, 200)

        content = json.loads(r.content)
        self.assertEqual(content['iid'], i.iid)
        self.assertEqual(content['status'], 'RESOLVED')

    def test_post_fixed_with_resolve_time(self):
        i = ItemFactory()
        i.save()
        r = self.c.post(
            self.url,
            dict(status='FIXED',
                 iid=i.iid,
                 email=i.assigned_user.userprofile.email,
                 resolve_time='1 hour',
                 comment="a comment")
            )
        self.assertEqual(r.status_code, 200)

        content = json.loads(r.content)
        self.assertEqual(content['iid'], i.iid)
        self.assertEqual(content['status'], 'RESOLVED')

    def test_post_comment(self):
        i = ItemFactory()
        i.save()
        r = self.c.post(
            self.url,
            dict(iid=i.iid,
                 email=i.assigned_user.userprofile.email,
                 comment="a comment")
            )
        self.assertEqual(r.status_code, 200)

        content = json.loads(r.content)
        self.assertEqual(content['iid'], i.iid)
        self.assertEqual(content['status'], 'OPEN')


class ItemTests(APITestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.item = ItemFactory()
        self.client.force_authenticate(user=self.u)

    def test_get(self):
        r = self.client.get(
            reverse('item-detail', kwargs={'pk': self.item.iid}))
        self.assertEqual(r.status_code, 200)

        # Loop through the simple attributes of the item
        for attr in ItemSerializer.Meta.fields:
            if (hasattr(self.item.__dict__, attr)):
                self.assertEqual(r.data[attr], self.item.__dict__[attr])

        # Verify accuracy of relationships
        self.assertEqual(self.item.owner_user.username,
                         r.data["owner_user"]['username'])
        self.assertEqual(self.item.assigned_user.username,
                         r.data["assigned_user"]['username'])

    def test_get_with_notification(self):
        self.notification = NotifyFactory(
            item=self.item, user=self.u)

        r = self.client.get(
            reverse('item-detail', kwargs={'pk': self.item.iid}))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['iid'], self.item.iid)

        usernames = [n.lower() for n in r.data['notifies']]
        self.assertIn(self.u.userprofile.username.lower(), usernames)


class ExternalAddItemTests(APITestCase):
    def setUp(self):
        self.title = 'Test item title'
        self.email = 'submission_email@example.com'
        self.name = 'Item Submitter'
        self.owner = UserProfileFactory()
        self.assignee = UserProfileFactory()
        self.project = ProjectFactory()
        self.milestone = MilestoneFactory(project=self.project)
        self.estimated_time = '1h'
        self.target_date = '2015-01-01'
        self.debug_info = 'debug info: zofjiojfojef'
        self.post_data = {
            'title': self.title,
            'email': self.email,
            'name': self.name,
            'pid': unicode(self.project.pk),
            'mid': unicode(self.milestone.pk),
            'type': 'action item',
            'owner': self.owner.username,
            'assigned_to': self.assignee.username,
            'estimated_time': self.estimated_time,
            'target_date': self.target_date,
            'debug_info': self.debug_info,
        }

        # Mock for passing the SafeOriginPermission
        self.remote_host = 'http://example.columbia.edu'

    def test_post_external_host_is_forbidden(self):
        r = self.client.post(reverse('external-add-item'),
                             {},
                             REMOTE_HOST='http://example.com')
        self.assertEqual(r.status_code, 403)

        r = self.client.post(reverse('external-add-item'),
                             self.post_data,
                             REMOTE_HOST='http://example.com')
        self.assertEqual(r.status_code, 403)

    def test_post_external_referrer_is_forbidden(self):
        r = self.client.post(reverse('external-add-item'),
                             {},
                             HTTP_REFERER='http://example.com')
        self.assertEqual(r.status_code, 403)

        r = self.client.post(reverse('external-add-item'),
                             self.post_data,
                             HTTP_REFERER='http://example.com')
        self.assertEqual(r.status_code, 403)

    def test_post_creates_action_item(self):
        r = self.client.post(reverse('external-add-item'),
                             self.post_data,
                             REMOTE_HOST=self.remote_host)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('title'), self.title)
        self.assertTrue(
            'Submitted by Item Submitter < submission_email@example.com >' in
            r.data.get('description')
        )
        self.assertEqual(r.data.get('type'), 'action item')
        self.assertEqual(self.owner.user.username,
                         r.data.get('owner_user')['username'])
        self.assertEqual(self.assignee.user.username,
                         r.data.get('assigned_user')['username'])
        self.assertTrue(self.debug_info in r.data.get('description'))
        self.assertTrue(unicode(self.milestone.pk) in r.data.get('milestone'))
        self.assertEqual(r.data.get('estimated_time'), '01:00:00')
        self.assertEqual(r.data.get('target_date'), self.target_date)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            '[PMT Item: {}] Attn: {} - {}'.format(
                self.project.name,
                self.assignee.fullname,
                self.title)
        )
        self.assertIn(self.owner.email, mail.outbox[0].to)
        self.assertIn(self.assignee.email, mail.outbox[0].to)

    def test_post_sends_email_even_when_owner_is_assignee(self):
        self.post_data['assigned_to'] = self.owner.username
        r = self.client.post(reverse('external-add-item'),
                             self.post_data,
                             REMOTE_HOST=self.remote_host)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('title'), self.title)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            '[PMT Item: {}] Attn: {} - {}'.format(
                self.project.name,
                self.owner.fullname,
                self.title)
        )
        self.assertEqual(
            mail.outbox[0].to,
            [self.owner.email, self.project.caretaker_user.userprofile.email])

    def test_post_redirects_client(self):
        redirect_url = 'http://example.com'
        self.post_data['redirect_url'] = redirect_url

        r = self.client.post(reverse('external-add-item'),
                             self.post_data,
                             REMOTE_HOST=self.remote_host)
        self.assertEqual(r.status_code, 302)
        self.assertRedirects(r, redirect_url, fetch_redirect_response=False)

    def test_post_referrer_permission(self):
        r = self.client.post(reverse('external-add-item'),
                             self.post_data,
                             HTTP_REFERER=self.remote_host)
        self.assertEqual(r.status_code, 200)

    def test_handles_missing_target_date(self):
        self.post_data['target_date'] = ''
        r = self.client.post(reverse('external-add-item'),
                             self.post_data,
                             REMOTE_HOST=self.remote_host)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('title'), self.title)
        self.assertTrue(
            'Submitted by Item Submitter < submission_email@example.com >' in
            r.data.get('description')
        )
        self.assertEqual(r.data.get('type'), 'action item')
        self.assertIn(
            unicode(self.owner.user.username),
            r.data.get('owner_user').values())
        self.assertIn(
            unicode(self.assignee.user.username),
            r.data.get('assigned_user').values())
        self.assertTrue(self.debug_info in r.data.get('description'))
        self.assertTrue(unicode(self.milestone.pk) in r.data.get('milestone'))
        self.assertEqual(r.data.get('estimated_time'), '01:00:00')

    def test_post_no_pid(self):
        del self.post_data['pid']
        r = self.client.post(reverse('external-add-item'),
                             self.post_data,
                             HTTP_REFERER=self.remote_host)
        self.assertEqual(r.status_code, 200)


class NotifyTests(APITestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.pu = self.u.userprofile
        self.item = ItemFactory()
        self.n = NotifyFactory(item=self.item, user=self.u)
        self.url = reverse("notify", kwargs={'pk': self.n.item.iid})

    def test_delete(self):
        self.client.login(username=self.u.username, password="test")
        r = self.client.delete(self.url)
        self.assertEqual(r.status_code, 204)

        notify = Notify.objects.filter(item=self.item, user=self.u)
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

        notify = Notify.objects.get(item=self.item, user=self.u)
        self.assertIsInstance(notify, Notify)

    def test_post_not_logged_in(self):
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 403)

    def test_put(self):
        self.client.login(username=self.u.username, password="test")
        r = self.client.put(self.url)
        self.assertEqual(r.status_code, 201)

        notify = Notify.objects.get(item=self.item, user=self.u)
        self.assertIsInstance(notify, Notify)

    def test_put_not_logged_in(self):
        r = self.client.put(self.url)
        self.assertEqual(r.status_code, 403)


class ProjectsTest(APITestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.client.force_authenticate(user=self.u)

        self.project1 = ProjectFactory(name='Project 1')
        self.project2 = ProjectFactory(name='Test Project 2')
        self.project3 = ProjectFactory(name='Testing number 3')
        self.project4 = ProjectFactory(name='abcdefg (project)')

    def test_get(self):
        r = self.client.get(reverse("project-list"))
        self.assertEqual(r.status_code, 200)

    def test_search(self):
        url = reverse('project-list')
        data = {'search': 'test'}
        r = self.client.get(url, data)
        self.assertEqual(r.status_code, 200)

        response = json.loads(r.content)
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0]['name'], self.project2.name)
        self.assertEqual(response[1]['name'], self.project3.name)

    def test_search_startswith(self):
        url = reverse('project-list')
        data = {'search': 'project'}
        r = self.client.get(url, data)
        self.assertEqual(r.status_code, 200)

        response = json.loads(r.content)
        self.assertEqual(len(response), 3)
        self.assertEqual(response[0]['name'], self.project1.name)
        self.assertEqual(response[1]['name'], self.project2.name)
        self.assertEqual(response[2]['name'], self.project4.name)

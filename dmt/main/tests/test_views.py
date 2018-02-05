import json
import unittest
import urllib
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from simpleduration import Duration
from .factories import (
    ActualTimeFactory,
    ClientFactory, ProjectFactory, MilestoneFactory,
    ItemFactory, NodeFactory, EventFactory, CommentFactory,
    UserProfileFactory, UserFactory,
    StatusUpdateFactory, NotifyFactory, GroupFactory,
    AttachmentFactory)
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils.dateparse import parse_date
from factory.fuzzy import FuzzyInteger
from waffle.models import Flag
from dmt.main.models import UserProfile as PMTUser
from dmt.main.models import (
    ActualTime, Events,
    Attachment, Comment, Item, ItemClient, Milestone, Project,
    Client, Notify, Reminder
)
from dmt.main.tests.support.mixins import LoggedInTestMixin


class BasicTest(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = UserFactory(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")

    def test_root(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoketest(self):
        self.c.get("/smoketest/")
        # smoketests should be run, but we
        # don't expect them to pass in a unit test env

    def test_search(self):
        response = self.c.get("/search/?q=foo")
        self.assertEquals(response.status_code, 200)

    def test_search_item(self):
        # Search terms need to be at least 3 characters long, so only
        # test this on items that have a sufficiently long ID.
        item = ItemFactory(iid=FuzzyInteger(100, 999999))
        params = urllib.urlencode({'q': item.iid})
        response = self.c.get('/search/?%s' % params)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Search for "%d"' % item.iid)
        self.assertContains(response, item.title)
        self.assertContains(response, item.get_absolute_url())

    def test_search_item2(self):
        item = ItemFactory(iid=FuzzyInteger(100, 999999))
        params = urllib.urlencode({'q': '#%d' % item.iid})
        response = self.c.get('/search/?%s' % params)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Search for "#%d"' % item.iid)
        self.assertContains(response, item.title)
        self.assertContains(response, item.get_absolute_url())

    def test_search_empty(self):
        response = self.c.get("/search/?q=")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "alert-danger")

    def test_dashboard(self):
        response = self.c.get("/dashboard/")
        self.assertEqual(response.status_code, 200)

    def test_owned_items(self):
        response = self.c.get(
            reverse('owned_items', args=[self.u.userprofile.username]))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Owned Items")


class TestClientViews(TestCase):
    def setUp(self):
        up = UserProfileFactory(username="testuser")
        self.u = up.user
        self.u.set_password("test")
        self.u.save()
        self.client.login(username=self.u.username, password="test")
        self.client_mock = ClientFactory()

    def test_client_detail_page(self):
        response = self.client.get(
            reverse('client_detail', args=(self.client_mock.client_id,)))
        self.assertEqual(response.status_code, 200)

    def test_client_items(self):
        item = ItemFactory()
        ItemClient.objects.create(item=item,
                                  client=self.client_mock)
        response = self.client.get(
            reverse('client_detail', args=(self.client_mock.client_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recent_items'].first(), item)

    def test_add_client_form(self):
        r = self.client.get(reverse('add_client'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Add New Client")

    @unittest.skipIf(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test has intermittent issues with PostgreSQL")
    def test_add_client(self):
        r = self.client.post(
            reverse('add_client', args=[]),
            dict(
                email='abc123@columbia.edu',
                lastname="testlastname",
                firstname="testfirstname",
                department="testdepartment",
                school="testschool",
            )
        )
        self.assertEqual(r.status_code, 302)
        c = Client.objects.get(email='abc123@columbia.edu')
        self.assertEqual(c.lastname, "testlastname")
        self.assertEqual(c.firstname, "testfirstname")
        self.assertEqual(c.department, "testdepartment")
        self.assertEqual(c.school, "testschool")
        self.assertEqual(c.status, "active")
        self.assertEqual(c.user, self.u)


class TestProjectViews(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestProjectViews, self).setUp()
        self.c = self.client
        self.p = ProjectFactory()

    def test_all_projects_page(self):
        r = self.c.get(reverse('project_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.p.name)
        self.assertContains(r, self.p.get_absolute_url())

    def test_project_page(self):
        r = self.c.get(self.p.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.p.name)

    def test_project_board(self):
        Flag.objects.create(name='project_board', everyone=True)
        r = self.c.get(self.p.get_absolute_url() + "board/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id="milestones"')

    def test_project_kanban(self):
        r = self.c.get(reverse('project_kanban', args=[self.p.pid]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id="milestones"')

    def test_project_report_page(self):
        r = self.c.get(self.p.get_absolute_url() + '#reports')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.p.name)

    def test_add_node(self):
        r = self.c.post(
            self.p.get_absolute_url() + "add_node/",
            dict(subject='node subject', body="this is the body"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(self.p.get_absolute_url())
        self.assertContains(r, "node subject")
        self.assertContains(r, "this is the body")

    def test_add_node_with_tags(self):
        r = self.c.post(
            self.p.get_absolute_url() + "add_node/",
            dict(subject='node subject', body="this is the body",
                 tags="tagone, tagtwo"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(self.p.get_absolute_url())
        self.assertContains(r, "node subject")
        self.assertContains(r, "this is the body")

    def test_add_node_empty_body(self):
        r = self.c.post(
            self.p.get_absolute_url() + "add_node/",
            dict(subject='node subject', body=""))
        self.assertEqual(r.status_code, 302)

    def test_add_status_update(self):
        r = self.c.post(
            self.p.get_absolute_url() + "add_update/",
            dict(body="xyzzy"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(self.p.get_absolute_url())
        self.assertContains(r, "xyzzy")

        r = self.c.get(self.u.userprofile.get_absolute_url())
        self.assertContains(r, "xyzzy")

        r = self.c.get("/status/")
        self.assertContains(r, "xyzzy")

    def test_add_status_empty_body(self):
        r = self.c.post(
            self.p.get_absolute_url() + "add_update/",
            dict(body=""))
        self.assertEqual(r.status_code, 302)

    def test_edit_statusupdate(self):
        s = StatusUpdateFactory()
        r = self.c.post(
            s.get_absolute_url(),
            dict(body="xyzzy"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(s.get_absolute_url())
        self.assertTrue("xyzzy" in r.content)

    def test_remove_user(self):
        u = UserProfileFactory()
        self.p.add_manager(u)
        r = self.c.get(
            self.p.get_absolute_url() + "remove_user/%s/" % u.username)
        self.assertTrue(u.fullname in r.content)
        self.assertTrue(u in self.p.managers())
        self.c.post(
            self.p.get_absolute_url() + "remove_user/%s/" % u.username)
        self.assertTrue(u not in self.p.managers())

    def test_add_personnel(self):
        u = UserProfileFactory(status='active')
        r = self.c.post(self.p.get_absolute_url() + "add_personnel/",
                        dict(personnel=[u.username]))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(u in self.p.all_personnel_in_project())

    def test_add_milestone(self):
        r = self.c.post(self.p.get_absolute_url() + "add_milestone/",
                        dict(name="NEW TEST MILESTONE",
                             description="NEW DESCRIPTION",
                             target_date="2020-01-01"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(self.p.get_absolute_url())
        self.assertTrue("NEW TEST MILESTONE" in r.content)
        m = Milestone.objects.get(name="NEW TEST MILESTONE")
        self.assertEqual(m.description, "NEW DESCRIPTION")

    def test_add_milestone_empty_date(self):
        r = self.c.post(self.p.get_absolute_url() + "add_milestone/",
                        dict(name="NEW TEST MILESTONE",
                             description="NEW DESCRIPTION",
                             target_date=""))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(self.p.get_absolute_url())
        self.assertContains(
            r,
            'The "NEW TEST MILESTONE" milestone wasn\'t created.')
        self.assertEqual(
            Milestone.objects.filter(name="NEW TEST MILESTONE").count(),
            0)

    def test_add_milestone_invalid_date(self):
        r = self.c.post(self.p.get_absolute_url() + "add_milestone/",
                        dict(name="NEW TEST MILESTONE",
                             description="NEW DESCRIPTION",
                             target_date="9j0934gj09g"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(self.p.get_absolute_url())
        self.assertContains(
            r,
            'The "NEW TEST MILESTONE" milestone wasn\'t created.')
        self.assertEqual(
            Milestone.objects.filter(name="NEW TEST MILESTONE").count(),
            0)

    def test_add_milestone_redirects_to_milestones_page(self):
        """ PMT #103894 """
        r = self.c.post(self.p.get_absolute_url() + "add_milestone/",
                        dict(name="NEW TEST MILESTONE",
                             target_date="2020-01-01"))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.url.endswith('#milestones'))

    def test_add_milestone_empty_title(self):
        r = self.c.post(self.p.get_absolute_url() + "add_milestone/",
                        dict(name="",
                             target_date="2020-01-01"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(self.p.get_absolute_url())
        self.assertTrue("Untitled milestone" in r.content)

    def test_add_action_item_empty_request(self):
        r = self.c.post(self.p.get_absolute_url() + "add_action_item/",
                        dict())
        self.assertEquals(r.status_code, 404)
        self.assertEquals(Reminder.objects.count(), 0)

    def test_timeline(self):
        r = self.c.get(reverse("project_timeline", args=[self.p.pid]))
        self.assertEqual(r.status_code, 200)

    def test_add_action_item_form_owner(self):
        milestone = MilestoneFactory()
        milestone.project.add_personnel(self.u.userprofile, auth='manager')
        r = self.c.get(milestone.project.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(
            r,
            'value="{}" selected="selected"'.format(
                self.u.userprofile.username))
        self.assertEqual(Reminder.objects.count(), 0)

    def test_add_action_item(self):
        u = UserProfileFactory()
        milestone = MilestoneFactory()

        r = self.c.post(
            milestone.project.get_absolute_url() + "add_action_item/",
            {
                "assigned_to": u.username,
                "milestone": milestone.mid,
                "owner": u.username,
                "estimated_time": "4h",
            }
        )
        self.assertEqual(r.status_code, 302)

        items = Item.objects.filter(milestone=milestone, assigned_user=u.user)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].assigned_user, u.user)
        self.assertEqual(items[0].title, "Untitled")
        self.assertEqual(items[0].estimated_time, timedelta(hours=4))
        self.assertEqual(Reminder.objects.count(), 0)

    def test_add_action_item_empty_title(self):
        u = UserProfileFactory()
        milestone = MilestoneFactory()

        r = self.c.post(milestone.project.get_absolute_url() +
                        "add_action_item/",
                        {"assigned_to": [u.username],
                         "milestone": milestone.mid,
                         "owner": u.username,
                         "title": ""})
        self.assertEqual(r.status_code, 302)

        items = Item.objects.filter(milestone=milestone, assigned_user=u.user)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].assigned_user, u.user)
        self.assertEqual(items[0].title, "Untitled")
        self.assertEqual(Reminder.objects.count(), 0)

    def test_add_action_item_multiple_assignees(self):
        u = UserProfileFactory()
        u2 = UserProfileFactory()
        u3 = UserProfileFactory()
        milestone = MilestoneFactory()

        r = self.c.post(
            reverse('add_action_item', args=(milestone.project.pk,)), {
                "assigned_to": [
                    u2.username,
                    u3.username,
                ],
                "milestone": milestone.mid,
                "owner": u.username,
                "title": "Test Action Item"
            })
        self.assertEqual(r.status_code, 302)

        items = Item.objects.filter(milestone=milestone, assigned_user=u2.user)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].assigned_user, u2.user)
        self.assertEqual(items[0].title, "Test Action Item")
        self.assertEqual(Reminder.objects.count(), 0)

        items = Item.objects.filter(milestone=milestone, assigned_user=u3.user)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].assigned_user, u3.user)
        self.assertEqual(items[0].title, "Test Action Item")
        self.assertEqual(Reminder.objects.count(), 0)

        self.assertNotEqual(
            Item.objects.filter(milestone=milestone,
                                assigned_user=u2.user).first(),
            Item.objects.filter(milestone=milestone,
                                assigned_user=u3.user).first())

    def test_add_action_item_owner(self):
        u = UserProfileFactory()
        milestone = MilestoneFactory()

        r = self.c.post(milestone.project.get_absolute_url() +
                        "add_action_item/",
                        {"assigned_to": [u.username],
                         "milestone": milestone.mid,
                         "owner": u.username})
        self.assertEqual(r.status_code, 302)

        items = Item.objects.filter(milestone=milestone, owner_user=u.user)
        self.assertEqual(len(items), 1)
        self.assertEqual(Reminder.objects.count(), 0)

    def test_add_action_item_with_reminder(self):
        u = UserProfileFactory()
        milestone = MilestoneFactory()

        url = reverse('add_action_item', args=(milestone.project.pk,))
        r = self.c.post(url, {
            'assigned_to': [u.username],
            'milestone': milestone.mid,
            'owner': u.username,
            'remind_me_toggle': 'on',
            'reminder_time': 2,
            'reminder_unit': 'd',
        })
        self.assertEqual(r.status_code, 302)

        items = Item.objects.filter(
            milestone=milestone,
            owner_user=u.user)
        i = items.first()
        self.assertEqual(len(items), 1)
        self.assertEqual(Reminder.objects.count(), 1)
        reminder = Reminder.objects.first()
        self.assertEqual(reminder.item, i)
        self.assertEqual(reminder.user, self.u)
        self.assertEqual(reminder.reminder_time, timedelta(days=2))

    def test_create_project_get(self):
        r = self.c.get(reverse('project_create'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue('Create new project' in r.content)

    def test_create_project_post(self):
        test_name = 'Test project'
        test_desc = 'Description for the test project'
        test_pub_view = True
        test_target_date = '2020-04-28'
        test_wiki_category = ''
        r = self.c.post(reverse('project_create'), {
            'name': test_name,
            'description': test_desc,
            'pub_view': test_pub_view,
            'target_date': test_target_date,
            'test_wiki_category': test_wiki_category
        })
        self.assertEqual(r.status_code, 302)
        url = r.url
        r = self.c.get(url)
        self.assertContains(r, test_name)
        self.assertContains(r, test_desc)

        p = Project.objects.get(name=test_name)
        # Assert that a Someday/Maybe milestone was created for
        # the project with the correct due date.
        someday_maybe = p.milestone_set.filter(name='Someday/Maybe').first()
        due_date = parse_date(test_target_date) + relativedelta(years=2)
        self.assertEqual(someday_maybe.target_date.year, due_date.year)
        self.assertEqual(someday_maybe.target_date.month, due_date.month)
        self.assertEqual(someday_maybe.target_date.day, due_date.day)

    def test_create_project_post_requires_project_name(self):
        r = self.c.post(reverse('project_create'),
                        {'description': 'description',
                         'pub_view': True,
                         'target_date': '2020-04-28',
                         'test_wiki_category': ''})
        self.assertEqual(r.status_code, 200)
        self.assertTrue('This field is required.' in r.content)

        r = self.c.post(reverse('project_create'),
                        {'name': '      ',
                         'description': 'description',
                         'pub_view': True,
                         'target_date': '2020-04-28',
                         'test_wiki_category': ''})
        self.assertEqual(r.status_code, 200)
        self.assertTrue('This field is required.' in r.content)

    def test_create_project_post_requires_target_date(self):
        r = self.c.post(reverse('project_create'),
                        {'name': 'Test project name',
                         'description': 'description',
                         'pub_view': True,
                         'test_wiki_category': ''})
        self.assertEqual(r.status_code, 200)
        self.assertTrue('This field is required.' in r.content)

    def test_create_project_post_requires_valid_target_date(self):
        r = self.c.post(reverse('project_create'),
                        {'name': 'Test project name',
                         'description': 'description',
                         'pub_view': True,
                         'target_date': '2309ur03j30',
                         'test_wiki_category': ''})
        self.assertEqual(r.status_code, 200)
        self.assertTrue('Invalid target date' in r.content)

    def test_create_project_post_private(self):
        self.c.post(reverse('project_create'),
                    {'name': 'Test project name',
                     'description': 'description',
                     'pub_view': False,
                     'target_date': '2020-04-28',
                     'test_wiki_category': ''})

    def test_create_project_post_adds_final_release_milestone(self):
        self.c.post(reverse('project_create'),
                    {'name': 'Test project name',
                     'description': 'description',
                     'pub_view': True,
                     'target_date': '2020-04-28',
                     'test_wiki_category': ''})
        p = Project.objects.get(name='Test project name')
        self.assertEqual(
            Milestone.objects.filter(project=p, name='Final Release').count(),
            1)

    def test_create_project_post_adds_someday_milestone(self):
        self.c.post(reverse('project_create'),
                    {'name': 'Test project name',
                     'description': 'description',
                     'pub_view': True,
                     'target_date': '2020-04-28',
                     'test_wiki_category': ''})
        p = Project.objects.get(name='Test project name')
        self.assertEqual(
            Milestone.objects.filter(project=p, name='Someday/Maybe').count(),
            1)

    def test_create_project_post_adds_current_user_to_personnel(self):
        self.c.post(reverse('project_create'),
                    {'name': 'Test project name',
                     'description': 'description',
                     'pub_view': True,
                     'target_date': '2020-04-28',
                     'test_wiki_category': ''})
        p = Project.objects.get(name='Test project name')
        self.assertTrue(self.u.userprofile in p.personnel_in_project())

    def test_edit_project_form(self):
        p = ProjectFactory()
        r = self.c.get(p.get_absolute_url() + "edit/")
        self.assertEqual(r.status_code, 200)

    def test_toggle_pin(self):
        p = ProjectFactory()
        self.assertEqual(p.projectpin_set.filter(user=self.u).count(), 0)
        self.c.post(reverse('project-pin', args=(p.pk,)))
        self.assertEqual(p.projectpin_set.filter(user=self.u).count(), 1)
        self.c.post(reverse('project-pin', args=(p.pk,)))
        self.assertEqual(p.projectpin_set.filter(user=self.u).count(), 0)


class TestItemUpdate(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestItemUpdate, self).setUp()
        self.c = self.client
        self.p = ProjectFactory()
        self.item = ItemFactory(owner_user=self.pu.user,
                                assigned_user=self.pu.user)
        self.formset_data = {
            'reminder_set-TOTAL_FORMS': 1,
            'reminder_set-INITIAL_FORMS': 0,
            'reminder_set-MIN_NUM_FORMS': 1,
            'reminder_set-MAX_NUM_FORMS': 1,
            'reminder_set-0-reminder_time': '',
            'reminder_set-0-item': self.item.pk,
        }
        self.url = reverse('item_update', args=(self.item.iid,))
        self.formdata = {
            'type': 'action item',
            'title': 'my title',
            'milestone': self.item.milestone.mid,
            'target_date': '2015-11-09',
            'estimated_time': '3h',
        }
        self.formdata.update(self.formset_data)

    def test_update_action_item(self):
        r = self.c.post(self.url, self.formdata)
        self.assertEqual(r.status_code, 302)

        self.item.refresh_from_db()
        self.assertEqual(self.item.type, 'action item')
        self.assertEqual(self.item.assigned_user.userprofile, self.pu)
        self.assertEqual(self.item.title, 'my title')
        self.assertEqual(self.item.target_date, parse_date('2015-11-09'))
        self.assertEqual(self.item.estimated_time, timedelta(hours=3))
        self.assertEqual(Reminder.objects.count(), 0)

        self.formdata.update({
            'target_date': '2015-11-12',
            'estimated_time': '5h 30m',
        })
        r = self.c.post(self.url, self.formdata)
        self.assertEqual(r.status_code, 302)

        self.item.refresh_from_db()
        self.assertEqual(self.item.type, 'action item')
        self.assertEqual(self.item.assigned_user.userprofile, self.pu)
        self.assertEqual(self.item.title, 'my title')
        self.assertEqual(self.item.target_date, parse_date('2015-11-12'))
        self.assertEqual(self.item.estimated_time,
                         timedelta(hours=5, minutes=30))
        self.assertEqual(Reminder.objects.count(), 0)

    def test_update_reminder(self):
        self.formdata.update({
            'reminder_set-0-reminder_time': '1d',
        })
        r = self.c.post(self.url, self.formdata)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Reminder.objects.count(), 1)

        reminder = Reminder.objects.first()
        self.assertEqual(reminder.user, self.u)
        self.assertEqual(reminder.item, self.item)
        self.assertEqual(reminder.reminder_time, timedelta(days=1))

        self.formdata.update({
            'reminder_set-0-reminder_time': '',
            'reminder_set-0-DELETE': 'on',
        })
        r = self.c.post(self.url, self.formdata)
        self.assertEqual(r.status_code, 302)
        # TODO why doesn't this work?
        # self.assertEqual(Reminder.objects.count(), 0)

    def test_update_null_target_date(self):
        self.formdata.update({
            'target_date': ''
        })

        r = self.c.post(self.url, self.formdata)
        self.assertEqual(r.status_code, 302)

        self.item.refresh_from_db()
        self.assertEqual(self.item.target_date,
                         self.item.milestone.target_date)


class MyProjectViewTests(TestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.client.login(username="testuser", password="test")

    def test_my_projects_page_in_project(self):
        p = ProjectFactory()
        p.add_personnel(self.u.userprofile)
        r = self.client.get(reverse('my_project_list'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(p.name in r.content)
        self.assertTrue(reverse('project_detail', args=(p.pid,)) in r.content)

    def test_project_view_queryparams(self):
        p = ProjectFactory()
        r = self.client.get(
            reverse('project_detail', args=(p.pid,)),
            {
                'interval_start': '2016-01-01',
                'interval_end': '',
            })
        self.assertEqual(r.status_code, 200)

        r = self.client.get(
            reverse('project_detail', args=(p.pid,)),
            {
                'interval_start': '',
                'interval_end': '2016-02-01',
            })
        self.assertEqual(r.status_code, 200)

        r = self.client.get(
            reverse('project_detail', args=(p.pid,)),
            {
                'interval_start': '',
                'interval_end': '',
            })
        self.assertEqual(r.status_code, 200)

    def test_my_projects_page_not_in_project(self):
        p = ProjectFactory()
        r = self.client.get(reverse('my_project_list'))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(p.name in r.content)

    def test_project_tag_list(self):
        p = ProjectFactory()
        r = self.client.get(reverse('project_tag_list', args=[p.pid]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue("Project Tags for" in r.content)

    def test_project_tag_detail(self):
        i = ItemFactory()
        i.tags.add("foo")
        r = self.client.get(
            reverse('project_tag', args=[i.milestone.project.pid, 'foo']))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, i.get_absolute_url())


class TestMilestoneViews(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")

    def test_project_page(self):
        m = MilestoneFactory()
        r = self.c.get(m.project.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(m.name in r.content)
        self.assertTrue(m.get_absolute_url() in r.content)

    def test_milestone_index(self):
        r = self.c.get("/milestone/")
        self.assertEqual(r.status_code, 200)

    def test_milestone_delete_form(self):
        m = MilestoneFactory()
        r = self.c.get(reverse('delete_milestone', args=(m.mid,)))
        self.assertEqual(r.status_code, 200)

    def test_milestone_delete(self):
        m = MilestoneFactory()
        p = m.project
        r = self.c.post(reverse('delete_milestone', args=(m.mid,)),
                        dict())
        self.assertEqual(r.status_code, 302)
        r = self.c.get(p.get_absolute_url())
        self.assertFalse(m.name in r.content)


class TestMilestoneDetailView(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestMilestoneDetailView, self).setUp()
        self.m = MilestoneFactory()

    def test_get(self):
        r = self.client.get(self.m.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.m.name)

    def test_get_with_items(self):
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        self.assertEqual(self.m.active_items().count(), 3)

        r = self.client.get(self.m.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.m.name)

        # Assert that the milestone page displays its items
        items = self.m.active_items().order_by('title')
        self.assertContains(r, items[0].title)
        self.assertContains(r, items[1].title)
        self.assertContains(r, items[2].title)

    def test_post_reassign_with_none_selected(self):
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        self.assertEqual(self.m.active_items().count(), 3)

        assignee = UserFactory()

        r = self.client.post(self.m.get_absolute_url(), {
            'action': 'assigned_to',
            'assigned_to': assignee.userprofile.pk,
        })
        self.assertEqual(r.status_code, 302)

        items = self.m.active_items().order_by('title')
        self.assertNotEqual(items[0].assigned_user, assignee)
        self.assertNotEqual(items[1].assigned_user, assignee)
        self.assertNotEqual(items[2].assigned_user, assignee)

        r = self.client.get(r.url)
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(
            r,
            'Assigned the following items to <strong>{}</strong>:'.format(
                assignee.userprofile.get_fullname()))

    def test_post_reassign_with_two_selected(self):
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        self.assertEqual(self.m.active_items().count(), 3)

        assignee = UserFactory()

        items = self.m.active_items().order_by('title')
        r = self.client.post(self.m.get_absolute_url(), {
            'action': 'assign',
            'assigned_to': assignee.userprofile.pk,
            '_selected_action': [items[0].pk, items[2].pk],
        })
        self.assertEqual(r.status_code, 302)

        self.assertEqual(items[0].assigned_user, assignee)
        self.assertNotEqual(items[1].assigned_user, assignee)
        self.assertEqual(items[2].assigned_user, assignee)

        r = self.client.get(r.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(
            r,
            'Assigned the following items to <strong>{}</strong>:'.format(
                assignee.userprofile.get_fullname()))

    def test_post_move_with_no_target_milestone(self):
        m2 = MilestoneFactory(project=self.m.project)
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        self.assertEqual(self.m.active_items().count(), 3)

        items = self.m.active_items().order_by('title')
        r = self.client.post(self.m.get_absolute_url(), {
            'action': 'move',
            'move_to': '',
            '_selected_action': [items[0].pk, items[2].pk],
        })
        self.assertEqual(r.status_code, 302)

        m1_items = self.m.active_items().order_by('title')
        m2_items = m2.active_items().order_by('title')
        self.assertEqual(m1_items.count(), 3)
        self.assertEqual(m2_items.count(), 0)

        r = self.client.get(r.url)
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(
            r,
            u'Moved the following items to <strong>{}</strong>:'.format(
                m2.name))

    def test_post_move_with_two_selected(self):
        m2 = MilestoneFactory(project=self.m.project)
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        self.assertEqual(self.m.active_items().count(), 3)

        items = self.m.active_items().order_by('title')
        r = self.client.post(self.m.get_absolute_url(), {
            'action': 'move',
            'move_to': m2.mid,
            '_selected_action': [items[0].pk, items[2].pk],
        })
        self.assertEqual(r.status_code, 302)

        m1_items = self.m.active_items().order_by('title')
        m2_items = m2.active_items().order_by('title')
        self.assertEqual(m1_items.count(), 1)
        self.assertEqual(m2_items.count(), 2)

        r = self.client.get(r.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(
            r,
            u'Moved the following items to <strong>{}</strong>:'.format(
                m2.name))

    def test_post_move_with_all_selected(self):
        # Make this an overdue milestone
        self.m.target_date = timezone.now().date() - timedelta(days=2)
        self.m.save()

        m2 = MilestoneFactory(project=self.m.project)
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        ItemFactory(milestone=self.m)
        self.assertEqual(self.m.active_items().count(), 3)

        items = self.m.active_items().order_by('title')
        r = self.client.post(self.m.get_absolute_url(), {
            'action': 'move',
            'move_to': m2.mid,
            '_selected_action': [items[0].pk, items[1].pk, items[2].pk],
        })
        self.assertEqual(r.status_code, 302)

        m1_items = self.m.active_items().order_by('title')
        m2_items = m2.active_items().order_by('title')
        self.assertEqual(m1_items.count(), 0)
        self.assertEqual(m2_items.count(), 3)

        self.m.refresh_from_db()
        m2.refresh_from_db()
        self.assertEqual(self.m.status, 'CLOSED')
        self.assertEqual(m2.status, 'OPEN')

        r = self.client.get(r.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(
            r,
            u'Moved the following items to <strong>{}</strong>:'.format(
                m2.name))

    def test_post_move_with_unicode(self):
        """ see PMT #111049 """
        m2 = MilestoneFactory(project=self.m.project,
                              name=u'\u201d')
        ItemFactory(milestone=self.m, title=u'\u201d')
        self.assertEqual(self.m.active_items().count(), 1)

        items = self.m.active_items().order_by('title')
        r = self.client.post(self.m.get_absolute_url(), {
            'action': 'move',
            'move_to': m2.mid,
            '_selected_action': [items[0].pk],
        })
        self.assertEqual(r.status_code, 302)

        m1_items = self.m.active_items().order_by('title')
        m2_items = m2.active_items().order_by('title')
        self.assertEqual(m1_items.count(), 0)
        self.assertEqual(m2_items.count(), 1)

        r = self.client.get(r.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(
            r, u'Moved the following items to <strong>{}</strong>:'.format(
                m2.name))


class TestItemViews(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestItemViews, self).setUp()
        self.c = self.client

    def test_item_view(self):
        i = ItemFactory()
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, i.title)

    def test_item_view_notification_present(self):
        Flag.objects.create(name='notification_ui', everyone=True)
        i = ItemFactory(assigned_user=self.u)
        n = NotifyFactory(item=i, user=self.u)
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "input_notification")
        self.assertTrue(r.context['assigned_to_current_user'])
        self.assertTrue(
            r.context['notifications_enabled_for_current_user'])
        self.assertItemsEqual(r.context['notified_users'], [n.user])

    def test_item_view_notification_not_present(self):
        Flag.objects.create(name='notification_ui', everyone=True)
        i = ItemFactory()
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "input_notification")
        self.assertFalse(r.context['assigned_to_current_user'])
        self.assertFalse(
            r.context['notifications_enabled_for_current_user'])
        self.assertEqual(len(r.context['notified_users']), 0)

    def test_milestone_view(self):
        i = ItemFactory()
        r = self.c.get(i.milestone.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, i.title)
        self.assertContains(r, i.get_absolute_url())

    def test_delete_item_view(self):
        i = ItemFactory()
        iid = i.iid
        milestone = i.milestone
        r = self.c.post(i.get_absolute_url() + "delete/")
        # should redirect us to the milestone
        self.assertEquals(r.status_code, 302)
        self.assertTrue(r['Location'].endswith(milestone.get_absolute_url()))
        # make sure it's gone
        q = Item.objects.filter(iid=iid)
        self.assertEquals(q.count(), 0)

    def test_delete_item_confirm(self):
        i = ItemFactory()
        r = self.c.get(i.get_absolute_url() + "delete/")
        self.assertEquals(r.status_code, 200)
        self.assertContains(r, "<form")

    def test_add_attachment(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "add_attachment/",
            dict(
                title="foo",
                description="blah",
                s3_url="https://s3/foo.jpg",
            ))
        self.assertEquals(r.status_code, 302)
        self.assertTrue(Attachment.objects.filter(
            item=i, url="https://s3/foo.jpg").exists())

    def test_delete_attachment_form(self):
        a = AttachmentFactory()
        r = self.c.get(reverse('delete_attachment', args=(a.id,)))
        self.assertEqual(r.status_code, 200)

    def test_delete_attachment(self):
        a = AttachmentFactory()
        r = self.c.post(reverse('delete_attachment', args=(a.id,)),
                        dict())
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Attachment.objects.filter(id=a.id).exists())

    def test_sign_s3_view(self):
        with self.settings(
                AWS_ACCESS_KEY='',
                AWS_SECRET_KEY='',
                AWS_S3_UPLOAD_BUCKET=''):
            r = self.c.get(
                '/sign_s3/?s3_object_name=default_name&s3_object_type=foo')
            self.assertEqual(r.status_code, 200)
            j = json.loads(r.content)
            self.assertTrue('signed_request' in j)

    def test_item_move_project(self):
        i = ItemFactory()
        m = MilestoneFactory()
        p = m.project
        r = self.c.get(reverse('item-move-project', args=(i.iid,)))
        self.assertEqual(r.status_code, 200)
        r = self.c.post(reverse('item-move-project', args=(i.iid,)),
                        dict(project=p.pid))
        self.assertEqual(r.status_code, 302)
        i = Item.objects.get(iid=i.iid)
        self.assertEqual(i.milestone.project.pid, p.pid)

    def test_item_set_milestone(self):
        i = ItemFactory()
        m = MilestoneFactory()
        r = self.c.post(reverse('set_item_milestone', args=(i.iid,)),
                        dict(mid=m.mid))
        self.assertEqual(r.status_code, 200)
        i = Item.objects.get(iid=i.iid)
        self.assertEqual(i.milestone.mid, m.mid)


class TestItemTagViews(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestItemTagViews, self).setUp()
        self.c = self.client

    def test_add_tag(self):
        i = ItemFactory()
        r = self.c.post(i.get_absolute_url() + "tag/",
                        dict(tags="tagone, tagtwo"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, "tagone")
        r = self.c.get("/tag/")
        self.assertContains(r, "tagone")
        r = self.c.get("/tag/tagone/")
        self.assertContains(r, "tagone")
        self.assertContains(r, str(i.iid))

    def test_remove_tag(self):
        i = ItemFactory()
        r = self.c.post(i.get_absolute_url() + "tag/",
                        dict(tags="tagone, tagtwo"))
        r = self.c.get(i.get_absolute_url() + "remove_tag/tagtwo/")
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertNotContains(r, "tagtwo")
        self.assertContains(r, "tagone")


class TestTagViews(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestTagViews, self).setUp()

    def test_merge_tags_form(self):
        i = ItemFactory()
        i.tags.add('testtag', 'testtag2')
        r = self.client.get(reverse('merge_tag', args=['testtag']))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'value="testtag2"')

    def test_merge_tags(self):
        i = ItemFactory()
        i.tags.add('testtag', 'testtag2')
        r = self.client.post(
            reverse('merge_tag', args=['testtag']),
            dict(tag='testtag2')
        )
        self.assertEqual(r.status_code, 302)
        i.refresh_from_db()
        self.assertEqual(len(i.tags.names()), 1)
        self.assertIn(u'testtag2', i.tags.names())


class TestItemWorkflow(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")

    def test_add_comment(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "comment/",
            dict(comment='this is a comment'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, "this is a comment")

    def test_add_comment_unicode(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "comment/",
            dict(comment=u'Here is a bullet point: \u2022'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, 'Here is a bullet point:')

    def test_add_comment_ccs_user(self):
        """ PMT #103873

        if a user comments on an item, they automatically
        get added to the CC list so they will receive followups.
        """
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "comment/",
            dict(comment='this is a comment'))
        self.assertEqual(r.status_code, 302)
        c = Notify.objects.filter(item=i, user=self.u).count()
        self.assertTrue(c > 0)

    def test_add_comment_markdown(self):
        i = ItemFactory()
        comment = '# testing\n\nhttp://example.com'
        r = self.c.post(
            i.get_absolute_url() + "comment/",
            dict(comment=comment))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, '<h1>testing</h1>')
        self.assertContains(r, '<a href="http://example.com"')

    def test_add_comment_empty(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "comment/",
            dict(comment=''))
        self.assertEqual(r.status_code, 302)

    def test_delete_own_comment(self):
        i = ItemFactory()
        e = EventFactory(item=i)
        comment = CommentFactory(
            item=i, event=e, username=self.u.userprofile.username)
        url = reverse('comment_delete', args=(comment.cid,))
        r = self.c.post(url)
        self.assertEqual(r.status_code, 302)

        # Assert that comment is really deleted
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(cid=comment.cid)

    def test_delete_someone_elses_comment(self):
        i = ItemFactory()
        e = EventFactory(item=i)
        comment = CommentFactory(item=i, event=e, username='someone_else')
        url = reverse('comment_delete', args=(comment.cid,))
        r = self.c.post(url)
        self.assertEqual(r.status_code, 403)

        # Assert that the comment still exists
        Comment.objects.get(cid=comment.cid)

    def test_update_own_comment(self):
        i = ItemFactory()
        e = EventFactory(item=i)
        comment = CommentFactory(
            item=i, event=e, username=self.u.userprofile.username)
        url = reverse('comment_update', args=(comment.cid,))
        r = self.c.post(url, {
            'comment_src': 'testing update'
        })
        self.assertEqual(r.status_code, 302)

        # Assert that comment was updated
        comment.refresh_from_db()
        self.assertEqual(comment.comment_src, 'testing update')
        self.assertEqual(comment.comment, '<p>testing update</p>\n')

    def test_update_someone_elses_comment(self):
        i = ItemFactory()
        e = EventFactory(item=i)
        comment = CommentFactory(item=i, event=e, username='someone_else')
        url = reverse('comment_update', args=(comment.cid,))
        r = self.c.post(url, {
            'comment_src': 'testing update'
        })
        self.assertEqual(r.status_code, 403)

        # Assert that the comment still exists
        Comment.objects.get(cid=comment.cid)
        comment.refresh_from_db()
        self.assertNotEqual(comment.comment_src, 'testing update')
        self.assertNotEqual(comment.comment, '<p>testing update</p>\n')

    def test_resolve(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "resolve/",
            dict(comment='this is a comment',
                 r_status='FIXED'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, "this is a comment")
        self.assertContains(r, "RESOLVED")
        self.assertContains(r, "FIXED")

    def test_resolve_with_time(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "resolve/",
            dict(comment='this is a comment',
                 time='2.5 hours',
                 r_status='FIXED'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, "this is a comment")
        self.assertContains(r, "RESOLVED")
        self.assertContains(r, "FIXED")
        self.assertContains(r, "2h 30m")

    def test_resolve_self_assigned(self):
        i = ItemFactory(owner_user=self.u,
                        assigned_user=self.u)
        r = self.c.post(
            i.get_absolute_url() + "resolve/",
            dict(comment='this is a comment',
                 r_status='FIXED'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, "this is a comment")
        self.assertContains(r, "VERIFIED")

    def test_inprogress(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "inprogress/",
            dict(comment='this is a comment'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, "this is a comment")
        self.assertContains(r, "INPROGRESS")

    def test_verify(self):
        i = ItemFactory(status='RESOLVED', r_status='FIXED')
        r = self.c.post(
            i.get_absolute_url() + "verify/",
            dict(comment='this is a comment'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, "this is a comment")
        self.assertContains(r, "VERIFIED")

    def test_reopen(self):
        i = ItemFactory(status='RESOLVED', r_status='FIXED')
        r = self.c.post(
            i.get_absolute_url() + "reopen/",
            dict(comment='this is a comment'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, "this is a comment")
        self.assertContains(r, "OPEN")

    def test_split(self):
        i = ItemFactory()
        cnt = Item.objects.all().count()
        r = self.c.post(
            i.get_absolute_url() + "split/",
            dict(title_0="sub item one",
                 title_1="sub item two",
                 title_2="sub item three"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, "VERIFIED")
        self.assertContains(r, "Split")
        self.assertContains(r, "sub item two")
        # make sure there are three more items now
        self.assertEqual(Item.objects.all().count(), cnt + 3)

        i.refresh_from_db()
        self.assertTrue(i.title.endswith(" (SPLIT)"))

    def test_split_bad_params(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "split/",
            dict(title_0="",
                 other_param="sub item two"))
        self.assertEqual(r.status_code, 302)

    def test_add_todos(self):
        i = ItemFactory()
        project = i.milestone.project
        r = self.c.post(
            project.get_absolute_url() + "add_todo/",
            dict(title_0="this is a todo",
                 tags="one two"))
        self.assertEqual(r.status_code, 302)

        r = self.c.get(project.get_absolute_url())
        self.assertContains(r, "this is a todo")

        i = Item.objects.get(title="this is a todo")
        self.assertEqual(i.owner_user, self.u)
        self.assertEqual(i.assigned_user, self.u)

    def test_add_todos_bad_params(self):
        i = ItemFactory()
        project = i.milestone.project
        r = self.c.post(
            project.get_absolute_url() + "add_todo/",
            dict(title_0="this is a todo",
                 some_other_param="foo",
                 title_1=""))
        self.assertEqual(r.status_code, 302)

    def test_add_bug(self):
        i = ItemFactory()
        project = i.milestone.project
        r = self.c.post(
            project.get_absolute_url() + "add_bug/",
            dict(title='test bug', description='test',
                 priority='1', milestone=i.milestone.mid,
                 assigned_to=i.assigned_user.userprofile.username,
                 tags="tagone, tagtwo"))
        r = self.c.get(project.get_absolute_url())
        self.assertContains(r, "test bug")

    def test_add_bug_no_tags(self):
        i = ItemFactory()
        project = i.milestone.project
        r = self.c.post(
            project.get_absolute_url() + "add_bug/",
            dict(title='test bug', description='test',
                 priority='1', milestone=i.milestone.mid,
                 owner=i.owner_user.userprofile.username,
                 assigned_to=i.assigned_user.userprofile.username,
                 tags=""))
        r = self.c.get(project.get_absolute_url())
        self.assertContains(r, "test bug")

    def test_change_priority(self):
        i = ItemFactory()
        r = self.c.get(i.get_absolute_url() + "priority/4/")
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, "CRITICAL")

    def test_reassign(self):
        i = ItemFactory()
        u = UserProfileFactory()
        r = self.c.post(i.get_absolute_url() + "assigned_to/",
                        dict(assigned_to=u.username))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, u.fullname)

    def test_change_owner(self):
        i = ItemFactory()
        u = UserProfileFactory()
        r = self.c.post(i.get_absolute_url() + "owner/",
                        dict(owner=u.username))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertContains(r, u.fullname)
        # make sure owner is in subscription list too
        all_notifies = [n.user for n in Notify.objects.filter(
            item=i.iid)]
        self.assertTrue(u.user in all_notifies)


class TestHistory(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = UserFactory(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")

    def test_item_view(self):
        i = ItemFactory()
        e1 = EventFactory(item=i)
        c1 = CommentFactory(item=i, event=e1)
        e2 = EventFactory(item=i)
        c2 = CommentFactory(item=i, event=e2)
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, c2.comment)
        self.assertContains(r, c1.comment)


class TestForum(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = UserFactory(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")

    def test_forum_index(self):
        r = self.c.get("/forum/")
        self.assertEqual(r.status_code, 200)

    def test_node(self):
        n = NodeFactory()
        r = self.c.get(n.get_absolute_url())
        self.assertEqual(r.status_code, 200)

    def test_node_reply(self):
        n = NodeFactory()
        r = self.c.post(
            n.get_absolute_url() + "reply/",
            dict(body="this is a comment"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(n.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue("this is a comment" in r.content)

    def test_node_reply_with_no_project(self):
        n = NodeFactory(replies=0)
        n.project = None
        n.project_id = None
        n.save()
        r = self.c.post(
            n.get_absolute_url() + "reply/",
            dict(body="this is a comment"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(n.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue("this is a comment" in r.content)

    def test_node_reply_empty_body(self):
        n = NodeFactory()
        r = self.c.post(
            n.get_absolute_url() + "reply/",
            dict(body=""))
        self.assertEqual(r.status_code, 302)

    def test_edit_node(self):
        n = NodeFactory()
        r = self.c.get(n.get_absolute_url() + "edit/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue("<form" in r.content)
        r = self.c.post(
            n.get_absolute_url() + "edit/",
            dict(subject='new subject', body='xyzzy'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(n.get_absolute_url())
        self.assertTrue("new subject" in r.content)
        self.assertTrue("xyzzy" in r.content)

    def test_delete_node(self):
        n = NodeFactory()
        r = self.c.get(n.get_absolute_url() + "delete/")
        self.assertTrue("<form" in r.content)
        r = self.c.post(
            n.get_absolute_url() + "delete/",
            params=dict())
        r = self.c.get(n.get_absolute_url())
        self.assertEquals(r.status_code, 404)

    def test_linkify_infinite_loop(self):
        # see https://pmt.ctl.columbia.edu/item/101115/
        n = NodeFactory(body=(
            '<a href="https://www1.columbia.edu/sec/cu/lweb/reserves/">'
            'https://www1.columbia.edu/sec/cu/lweb/reserves/</a>. '
            'Instructors can also email film requests to butlres@lib'
            'raries.cul.columbia.edu'))
        r = self.c.get(n.get_absolute_url())
        self.assertEqual(r.status_code, 200)


class TestForumTagViews(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")

    def test_add_tag(self):
        i = NodeFactory()
        r = self.c.post(i.get_absolute_url() + "tag/",
                        dict(tags="tagone, tagtwo"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue("tagone" in r.content)
        r = self.c.get("/tag/")
        self.assertTrue("tagone" in r.content)
        r = self.c.get("/tag/tagone/")
        self.assertTrue("tagone" in r.content)
        self.assertTrue(str(i.nid) in r.content)

    def test_remove_tag(self):
        i = NodeFactory()
        r = self.c.post(i.get_absolute_url() + "tag/",
                        dict(tags="tagone, tagtwo"))
        r = self.c.get(i.get_absolute_url() + "remove_tag/tagtwo/")
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue("tagtwo" not in r.content)
        self.assertTrue("tagone" in r.content)


class TestFeeds(TestCase):
    def setUp(self):
        self.c = self.client

    def test_forum_feed(self):
        NodeFactory()
        r = self.c.get("/feeds/forum/rss/")
        self.assertEquals(r.status_code, 200)

    def test_status_feed(self):
        s = StatusUpdateFactory()
        r = self.c.get("/feeds/status/")
        self.assertEquals(r.status_code, 200)
        self.assertTrue("<author>{} ({})</author>".format(
            s.author.userprofile.email,
            s.author.userprofile.get_fullname()) in r.content)
        self.assertTrue("<pubDate>{}</pubDate>".format(
            s.added.strftime("%a, %d %b %Y %H:%M:%S %z")) in r.content)
        self.assertTrue("<content:encoded>" in r.content)

    def test_project_feed(self):
        p = ProjectFactory()
        ItemFactory()
        r = self.c.get("/feeds/project/%s/" % p.pid)
        self.assertEquals(r.status_code, 200)

    @override_settings(BASE_URL="https://newbase.com")
    def test_base_url(self):
        i = ItemFactory()
        r = self.c.get("/feeds/project/%s/" % i.milestone.project.pid)
        self.assertEquals(r.status_code, 200)
        self.assertNotContains(r, "dmt.ccnmtl.columbia.edu")
        self.assertContains(r, "https://newbase.com")

        StatusUpdateFactory()
        r = self.c.get("/feeds/status/")
        self.assertNotContains(r, "dmt.ccnmtl.columbia.edu")
        self.assertContains(r, "https://newbase.com")
        self.assertContains(r, "<link>https://newbase.com/project")

        NodeFactory()
        r = self.c.get("/feeds/forum/rss/")
        self.assertNotContains(r, "dmt.ccnmtl.columbia.edu")
        self.assertContains(r, "https://newbase.com")


class TestDRFViews(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = UserFactory(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")

    def test_clients_list(self):
        r = self.c.get("/drf/clients/")
        self.assertEqual(r.status_code, 200)

    def test_projects_list(self):
        r = self.c.get("/drf/projects/")
        self.assertEqual(r.status_code, 200)

    def test_users_list(self):
        r = self.c.get("/drf/users/")
        self.assertEqual(r.status_code, 200)

    def test_milestones_list(self):
        r = self.c.get("/drf/milestones/")
        self.assertEqual(r.status_code, 200)

    def test_items_list(self):
        r = self.c.get("/drf/items/")
        self.assertEqual(r.status_code, 200)

    def test_project_milestones_list(self):
        p = ProjectFactory()
        r = self.c.get("/drf/projects/%d/milestones/" % p.pid)
        self.assertEqual(r.status_code, 200)

    def test_milestone_items_list(self):
        m = MilestoneFactory()
        r = self.c.get("/drf/milestones/%d/items/" % m.mid)
        self.assertEqual(r.status_code, 200)


class GroupTest(TestCase):
    def setUp(self):
        self.u = UserFactory(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.client.login(username="testuser", password="test")
        self.group = GroupFactory()
        self.u.userprofile.primary_group = self.group.grp
        self.u.userprofile.save()

    def test_group_list(self):
        response = self.client.get(reverse('group_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(self.group) in response.content)

    def test_group_detail(self):
        inactive_user = UserProfileFactory(
            username='inactive_user', status='inactive')
        inactive_user.primary_group = self.group.grp
        inactive_user.save()

        response = self.client.get(
            reverse('group_detail', args=(self.group.grp.username,)))
        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            self.u.userprofile in response.context['primary_members'])
        self.assertNotIn(inactive_user, response.context['primary_members'])
        self.assertEqual(
            response.context['primary_members'].count(), 1)

        self.assertTrue(
            self.group.username in response.context['other_members'])
        self.assertNotIn(inactive_user, response.context['other_members'])
        self.assertEqual(
            response.context['other_members'].count(), 1)

        self.assertTrue(
            self.u.userprofile in response.context['eligible_users'])
        self.assertNotIn(inactive_user, response.context['eligible_users'])
        self.assertEqual(
            response.context['eligible_users'].count(), 1)

        self.assertTrue(str(self.group) in response.content)
        self.assertTrue(self.group.username.username in response.content)

    def test_remove_user_from_group(self):
        grp_username = self.group.grp.username
        user_username = self.group.username.username
        r = self.client.post(
            reverse('remove_user_from_group', args=(grp_username,)),
            dict(username=user_username))
        self.assertEqual(r.status_code, 302)
        r = self.client.get(
            reverse('group_detail', args=(grp_username,)))
        user_url = self.group.username.get_absolute_url()
        self.assertFalse(user_url in r.content)

    def test_add_user_to_group(self):
        grp_username = self.group.grp.username
        u = UserProfileFactory()
        r = self.client.post(
            reverse('add_user_to_group', args=(grp_username,)),
            dict(username=u.username))
        self.assertEqual(r.status_code, 302)
        r = self.client.get(
            reverse('group_detail', args=(grp_username,)))
        self.assertTrue(u.get_absolute_url() in r.content)

    def test_create_group(self):
        r = self.client.post(reverse('group_create'), dict(group='foo'))
        self.assertEqual(r.status_code, 302)
        r = self.client.get(reverse('group_list'))
        self.assertTrue('grp_foo' in r.content)

    def test_nonexistent_group(self):
        r = self.client.get(reverse('group_detail', args=('not_real',)))
        self.assertTrue(r.status_code, 404)


class UserTest(TestCase):
    def setUp(self):
        self.u = User.objects.create(
            username="testuser",
            is_superuser=True)
        self.u.set_password("test")
        self.u.save()
        self.client.login(username="testuser", password="test")

    def test_deactivate_user_form(self):
        u = UserProfileFactory(status='active')
        r = self.client.get(u.get_absolute_url() + "deactivate/")
        self.assertEqual(r.status_code, 200)

    def test_deactivate_simple(self):
        u = UserProfileFactory(status='active')
        r = self.client.post(u.get_absolute_url() + "deactivate/",
                             dict())
        self.assertEqual(r.status_code, 302)
        u = PMTUser.objects.get(username=u.username)
        self.assertFalse(u.active())

    def test_deactivate_populated(self):
        u = UserProfileFactory(status='active')
        # this user actually has some stuff
        p = ProjectFactory(caretaker_user=u.user)
        assigned = ItemFactory(assigned_user=u.user)
        owned = ItemFactory(owner_user=u.user)
        # reassign it to the request user
        params = dict()
        params["project_%d" % p.pid] = self.u.userprofile.username
        params[
            "item_assigned_%d" % assigned.iid] = self.u.userprofile.username
        params["item_owner_%d" % owned.iid] = self.u.userprofile.username
        r = self.client.post(
            u.get_absolute_url() + "deactivate/",
            params)
        self.assertEqual(r.status_code, 302)
        u = PMTUser.objects.get(username=u.username)
        self.assertFalse(u.active())

        # refetch and check
        p = Project.objects.get(pid=p.pid)
        self.assertEqual(p.caretaker_user, self.u)

        assigned = Item.objects.get(iid=assigned.iid)
        self.assertEqual(assigned.assigned_user, self.u)

        owned = Item.objects.get(iid=owned.iid)
        self.assertEqual(owned.owner_user, self.u)

    def test_timeline(self):
        u = UserProfileFactory()
        r = self.client.get(reverse("user_timeline", args=[u.username]))
        self.assertEqual(r.status_code, 200)


class TestAddTrackersView(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestAddTrackersView, self).setUp()

        self.project = ProjectFactory(caretaker_user=self.u)
        self.project2 = ProjectFactory(caretaker_user=self.u)
        self.project3 = ProjectFactory(caretaker_user=self.u)
        MilestoneFactory(project=self.project)
        MilestoneFactory(project=self.project2)
        MilestoneFactory(project=self.project3)
        self.valid_post_data = {
            # Formset's management form
            'form-TOTAL_FORMS': 10,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,

            'form-0-project': self.project.pk,
            'form-0-task': 'test',
            'form-0-time': '3hr',
            'form-0-client-uni': '',

            'form-1-project': self.project2.pk,
            'form-1-task': 'test project 2',
            'form-1-time': '2hr',
            'form-1-client-uni': '',

            'form-2-project': self.project3.pk,
            'form-2-task': 'test project 3',
            'form-2-time': '15m',
            'form-2-client-uni': '',
        }

    def test_add_trackers_view(self):
        r = self.client.get(reverse('add_trackers'))
        self.assertEqual(r.status_code, 200)

    def test_add_trackers_post_empty(self):
        r = self.client.post(reverse('add_trackers'), {
            # Formset's management form
            'form-TOTAL_FORMS': 10,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        })
        self.assertEqual(r.status_code, 302)

    def test_add_trackers_post_multiple(self):
        r = self.client.post(reverse('add_trackers'), self.valid_post_data)

        self.assertEqual(r.status_code, 302)

        r = self.client.get(r.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Tracker added')
        self.assertContains(r, self.project.name)

        items = Item.objects.reverse()[:3]

        for i in range(3):
            self.assertEqual(
                items[i].title,
                self.valid_post_data['form-%d-task' % i])
            self.assertEqual(
                items[i].milestone.project.pk,
                self.valid_post_data['form-%d-project' % i])
            self.assertEqual(
                items[i].get_resolve_time(),
                Duration(self.valid_post_data['form-%d-time' % i]).timedelta())

    def test_add_trackers_post_single(self):
        params = self.valid_post_data.copy()
        params.update({
            'form-1-project': '',
            'form-1-task': '',
            'form-1-time': '',
            'form-1-client-uni': '',

            'form-2-project': '',
            'form-2-task': '',
            'form-2-time': '',
            'form-2-client-uni': '',
        })

        r = self.client.post(reverse('add_trackers'), params)

        self.assertEqual(r.status_code, 302)

        r = self.client.get(r.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Tracker added')
        self.assertContains(r, self.project.name)

        i = Item.objects.last()
        self.assertEqual(i.title, self.valid_post_data['form-0-task'])
        self.assertEqual(
            i.milestone.project.pk,
            self.valid_post_data['form-0-project'])
        self.assertEqual(
            i.get_resolve_time(),
            Duration(self.valid_post_data['form-0-time']).timedelta())

    def test_add_trackers_post_tracker_invalid(self):
        params = self.valid_post_data.copy()
        params.update({
            'form-0-project': '',
            'form-0-time': '',

            'form-1-project': '',
            'form-1-time': '',

            'form-2-project': '',
            'form-2-time': ''
        })

        r = self.client.post(reverse('add_trackers'), params)
        self.assertEqual(r.status_code, 200)

        r = self.client.get(reverse('add_trackers'))
        self.assertNotContains(r, 'Tracker added')


class TestUserViews(LoggedInTestMixin, TestCase):
    def test_user_list_page(self):
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)

    def test_user_form_page(self):
        response = self.client.get(reverse('user_edit',
                                           args=[self.u.userprofile.username]))
        self.assertEqual(response.status_code, 200)

    def test_user_list_status_filter(self):
        u1 = UserProfileFactory(status='active')
        u2 = UserProfileFactory(status='inactive')
        r = self.client.get(
            reverse('user_list') + "?status=active")
        self.assertTrue(u1.username in r.content)
        self.assertFalse(u2.username in r.content)

        r = self.client.get(
            reverse('user_list') + "?status=inactive")
        self.assertFalse(u1.username in r.content)
        self.assertTrue(u2.username in r.content)


class TestActualTimeDeletion(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")

    def test_delete_own_time(self):
        i = ItemFactory()
        time = ActualTimeFactory(item=i, user=self.u)
        url = reverse('delete_time', args=(time.uuid,))
        r = self.c.post(url)
        self.assertEqual(r.status_code, 302)

        with self.assertRaises(ActualTime.DoesNotExist):
            ActualTime.objects.get(uuid=time.uuid)

    def test_delete_someone_elses_time(self):
        i = ItemFactory()
        time = ActualTimeFactory(item=i, user=UserFactory())
        url = reverse('delete_time', args=(time.uuid,))
        r = self.c.post(url)
        self.assertEqual(r.status_code, 403)

        ActualTime.objects.get(uuid=time.uuid)


class TestItemAddSubscriberView(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestItemAddSubscriberView, self).setUp()
        self.i = ItemFactory()

    def test_post_no_subscriber(self):
        self.assertEqual(Notify.objects.count(), 0)
        url = reverse('add_subscriber', args=(self.i.pk,))
        r = self.client.post(url, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'No subscriber provided.')
        self.assertEqual(Notify.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_post(self):
        subscriber = UserFactory()
        self.assertEqual(Notify.objects.count(), 0)
        url = reverse('add_subscriber', args=(self.i.pk,))
        r = self.client.post(url, {
            'subscriber': subscriber
        }, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(
            r,
            '<strong>{}</strong> has been subscribed to this item.'.format(
                subscriber.userprofile.get_fullname()))
        self.assertEqual(Notify.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(email.subject, '[PMT Item] {}'.format(self.i.title))

        body = '{} has subscribed you to this PMT item:\n\t{}\n'.format(
            unicode(self.u.userprofile),
            'https://pmt.ctl.columbia.edu{}'.format(
                self.i.get_absolute_url()))
        self.assertEqual(email.body, body)

        self.assertEqual(email.to, [subscriber.userprofile.get_email()])

    def test_post_subscribe_self(self):
        subscriber = self.u
        self.assertEqual(Notify.objects.count(), 0)
        url = reverse('add_subscriber', args=(self.i.pk,))
        r = self.client.post(url, {
            'subscriber': subscriber
        }, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(
            r,
            '<strong>{}</strong> has been subscribed to this item.'.format(
                unicode(subscriber.userprofile)))
        self.assertEqual(Notify.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_already_subscribed(self):
        n = NotifyFactory(item=self.i)
        self.assertEqual(Notify.objects.count(), 1)
        url = reverse('add_subscriber', args=(self.i.pk,))
        r = self.client.post(url, {
            'subscriber': n.user.username
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Notify.objects.count(), 1)


class TestItemCreateView(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestItemCreateView, self).setUp()
        self.milestone = MilestoneFactory()
        self.form_data = {
            'title': 'My Action Item',
            'project': self.milestone.project.pk,
            'milestone': self.milestone.pk,
            'created_by': self.u.pk,
            'owner_user': self.u.pk,
            'assigned_user': self.u.pk,
            'priority': 1,
            'target_date': self.milestone.target_date,
            'estimated_time': '3h',
            'tags': ['testtag'],
            'description': 'item description',
            'status': 'OPEN',
            'type': 'action item',
        }

    def test_get_with_milestone(self):
        url = reverse('item_create') + '?mid={}'.format(self.milestone.mid)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_get_no_milestone(self):
        url = reverse('item_create')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['messages']), 1)
        m = list(r.context['messages'])[0]
        self.assertEqual(m.message, 'Couldn\'t find project or milestone.')

    def test_post(self):
        inactive_user = UserFactory(is_active=False)
        active_user = UserFactory()
        self.form_data['assigned_user'] = inactive_user
        url = reverse('item_create') + '?mid={}'.format(self.milestone.mid)
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)
        self.assertFormError(
            r, 'form', 'assigned_user',
            'Select a valid choice. That choice is not '
            'one of the available choices.')

        self.form_data['assigned_user'] = active_user.pk
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Item.objects.count(), 1)
        item = Item.objects.first()
        self.assertEqual(Events.objects.filter(item=item).count(), 1)
        event = Events.objects.filter(item=item).first()
        self.assertEqual(event.status, 'OPEN')
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(
            email.subject,
            '[PMT Item: {}] Attn: {} - {}'.format(
                item.milestone.project.name,
                active_user.userprofile.get_fullname(),
                item.title))
        self.assertIn(item.milestone.project.name, email.body)
        self.assertIn(item.milestone.name, email.body)
        self.assertIn(active_user.userprofile.get_fullname(), email.body)
        self.assertIn('Action item added', email.body)

        self.assertEqual(item.milestone.project, self.milestone.project)
        self.assertEqual(item.milestone, self.milestone)
        self.assertEqual(item.owner_user, self.u)
        self.assertEqual(item.created_by, self.u)
        self.assertEqual(item.assigned_user, active_user)
        self.assertEqual(item.priority, 1)
        self.assertEqual(item.target_date, self.milestone.target_date)
        self.assertEqual(item.estimated_time, timedelta(hours=3))
        self.assertEqual(item.tags.first().name, 'testtag')
        self.assertEqual(item.description, 'item description')

    def test_post_no_milestone_in_url(self):
        del self.form_data['milestone']
        url = reverse('item_create')
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)
        self.assertFormError(r, 'form', 'milestone', 'This field is required.')

    def test_post_no_milestone(self):
        del self.form_data['milestone']
        url = reverse('item_create') + '?mid={}'.format(self.milestone.mid)
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)
        self.assertFormError(r, 'form', 'milestone', 'This field is required.')

    def test_post_no_project(self):
        del self.form_data['project']
        url = reverse('item_create') + '?mid={}'.format(self.milestone.mid)
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)
        self.assertFormError(r, 'form', 'project', 'This field is required.')

    def test_post_null_target_date(self):
        self.form_data.update({
            'target_date': ''
        })
        url = reverse('item_create') + '?mid={}'.format(self.milestone.mid)
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 302)

        item = Item.objects.first()
        self.assertEqual(item.target_date, item.milestone.target_date)


class TestBugCreateView(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestBugCreateView, self).setUp()
        self.milestone = MilestoneFactory()
        self.form_data = {
            'title': 'My Bug',
            'project': self.milestone.project.pk,
            'milestone': self.milestone.pk,
            'created_by': self.u.pk,
            'owner_user': self.u.pk,
            'assigned_user': self.u.pk,
            'priority': 1,
            'target_date': self.milestone.target_date,
            'tags': ['testtag'],
            'description': 'item description',
            'status': 'OPEN',
            'type': 'bug',
        }

    def test_get_with_milestone(self):
        url = reverse('bug_create') + '?mid={}'.format(self.milestone.mid)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_get_no_milestone(self):
        url = reverse('bug_create')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['messages']), 1)
        m = list(r.context['messages'])[0]
        self.assertEqual(m.message, 'Couldn\'t find project or milestone.')

    def test_post(self):
        inactive_user = UserFactory(is_active=False)
        active_user = UserFactory()
        self.form_data['assigned_user'] = inactive_user
        url = reverse('bug_create') + '?mid={}'.format(self.milestone.mid)
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)
        self.assertFormError(
            r, 'form', 'assigned_user',
            'Select a valid choice. That choice is not '
            'one of the available choices.')

        self.form_data['assigned_user'] = active_user.pk
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Item.objects.count(), 1)
        item = Item.objects.first()
        self.assertEqual(Events.objects.filter(item=item).count(), 1)
        event = Events.objects.filter(item=item).first()
        self.assertEqual(event.status, 'OPEN')
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(
            email.subject,
            '[PMT Item: {}] Attn: {} - {}'.format(
                item.milestone.project.name,
                active_user.userprofile.get_fullname(),
                item.title))
        self.assertIn(item.milestone.project.name, email.body)
        self.assertIn(item.milestone.name, email.body)
        self.assertIn(active_user.userprofile.get_fullname(), email.body)
        self.assertIn('My Bug', email.body)

        self.assertEqual(item.milestone.project, self.milestone.project)
        self.assertEqual(item.milestone, self.milestone)
        self.assertEqual(item.owner_user, self.u)
        self.assertEqual(item.created_by, self.u)
        self.assertEqual(item.assigned_user, active_user)
        self.assertEqual(item.priority, 1)
        self.assertEqual(item.target_date, self.milestone.target_date)
        self.assertEqual(item.tags.first().name, 'testtag')
        self.assertEqual(item.description, 'item description')

    def test_post_no_milestone_in_url(self):
        del self.form_data['milestone']
        url = reverse('bug_create')
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)
        self.assertFormError(r, 'form', 'milestone', 'This field is required.')

    def test_post_no_milestone(self):
        del self.form_data['milestone']
        url = reverse('bug_create') + '?mid={}'.format(self.milestone.mid)
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)
        self.assertFormError(r, 'form', 'milestone', 'This field is required.')

    def test_post_no_project(self):
        del self.form_data['project']
        url = reverse('bug_create') + '?mid={}'.format(self.milestone.mid)
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)
        self.assertFormError(r, 'form', 'project', 'This field is required.')

    def test_post_null_target_date(self):
        self.form_data.update({
            'target_date': ''
        })
        url = reverse('bug_create') + '?mid={}'.format(self.milestone.mid)
        r = self.client.post(url, self.form_data)
        self.assertEqual(r.status_code, 302)

        item = Item.objects.first()
        self.assertEqual(item.target_date, item.milestone.target_date)

import json
import unittest
import urllib

from simpleduration import Duration
from .factories import (
    ClientFactory, ProjectFactory, MilestoneFactory,
    ItemFactory, NodeFactory, EventFactory, CommentFactory,
    UserProfileFactory, UserFactory,
    StatusUpdateFactory, NotifyFactory, GroupFactory,
    AttachmentFactory)
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from factory.fuzzy import FuzzyInteger
from waffle.models import Flag
from dmt.main.models import UserProfile as PMTUser
from dmt.main.models import (
    Attachment, Comment, Item, ItemClient, Milestone, Project,
    Client
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
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
        assert "PASS" in response.content

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
        self.assertTrue("alert-danger" in response.content)

    def test_dashboard(self):
        response = self.c.get("/dashboard/")
        self.assertEqual(response.status_code, 200)

    def test_owned_items(self):
        response = self.c.get(
            reverse('owned_items', args=[self.u.userprofile.username]))
        self.assertEquals(response.status_code, 200)
        self.assertTrue("Owned Items" in response.content)


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
        self.assertTrue("Add New Client" in r.content)

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
        self.assertEqual(c.contact, self.u.userprofile)
        self.assertEqual(c.user, self.u)


class TestProjectViews(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestProjectViews, self).setUp()
        self.c = self.client
        self.p = ProjectFactory()

    def test_all_projects_page(self):
        r = self.c.get(reverse('project_list'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(self.p.name in r.content)
        self.assertTrue(self.p.get_absolute_url() in r.content)

    def test_project_page(self):
        r = self.c.get(self.p.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.p.name)

    def test_project_board(self):
        Flag.objects.create(name='project_board', everyone=True)
        r = self.c.get(self.p.get_absolute_url() + "board/")
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
        self.assertTrue("node subject" in r.content)
        self.assertTrue("this is the body" in r.content)

    def test_add_node_with_tags(self):
        r = self.c.post(
            self.p.get_absolute_url() + "add_node/",
            dict(subject='node subject', body="this is the body",
                 tags="tagone, tagtwo"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(self.p.get_absolute_url())
        self.assertTrue("node subject" in r.content)
        self.assertTrue("this is the body" in r.content)

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
        self.assertTrue("xyzzy" in r.content)

        r = self.c.get(self.u.userprofile.get_absolute_url())
        self.assertTrue("xyzzy" in r.content)

        r = self.c.get("/status/")
        self.assertTrue("xyzzy" in r.content)

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

    def test_add_user(self):
        u = UserProfileFactory(status='active')
        r = self.c.post(self.p.get_absolute_url() + "add_user/",
                        dict(username=u.username))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(u in self.p.all_personnel_in_project())

    def test_add_milestone(self):
        r = self.c.post(self.p.get_absolute_url() + "add_milestone/",
                        dict(name="NEW TEST MILESTONE",
                             target_date="2020-01-01"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(self.p.get_absolute_url())
        self.assertTrue("NEW TEST MILESTONE" in r.content)

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

    def test_timeline(self):
        r = self.c.get(reverse("project_timeline", args=[self.p.pid]))
        self.assertEqual(r.status_code, 200)

    def test_add_action_item_form_owner(self):
        milestone = MilestoneFactory()
        milestone.project.add_personnel(self.u.userprofile, auth='manager')
        r = self.c.get(milestone.project.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(
            "value=\"testuser\" selected=\"selected\"" in r.content)

    def test_add_action_item(self):
        u = UserProfileFactory()
        milestone = MilestoneFactory()

        r = self.c.post(milestone.project.get_absolute_url() +
                        "add_action_item/",
                        {"assigned_to": u.username,
                         "milestone": milestone.mid,
                         "owner": u.username})
        self.assertEqual(r.status_code, 302)

        items = Item.objects.filter(milestone=milestone, assigned_to=u)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].assigned_to, u)
        self.assertEqual(items[0].assigned_user, u.user)
        self.assertEqual(items[0].title, "Untitled")

    def test_add_action_item_empty_title(self):
        u = UserProfileFactory()
        milestone = MilestoneFactory()

        r = self.c.post(milestone.project.get_absolute_url() +
                        "add_action_item/",
                        {"assigned_to": u.username,
                         "milestone": milestone.mid,
                         "owner": u.username,
                         "title": ""})
        self.assertEqual(r.status_code, 302)

        items = Item.objects.filter(milestone=milestone, assigned_to=u)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].assigned_to, u)
        self.assertEqual(items[0].assigned_user, u.user)
        self.assertEqual(items[0].title, "Untitled")

    def test_add_action_item_owner(self):
        u = UserProfileFactory()
        milestone = MilestoneFactory()

        r = self.c.post(milestone.project.get_absolute_url() +
                        "add_action_item/",
                        {"assigned_to": u.username,
                         "milestone": milestone.mid,
                         "owner": u.username})
        self.assertEqual(r.status_code, 302)

        items = Item.objects.filter(milestone=milestone, owner=u,
                                    owner_user=u.user)
        self.assertEqual(len(items), 1)

    def test_create_project_get(self):
        r = self.c.get(reverse('project_create'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue('Create new project' in r.content)

    def test_create_project_post(self):
        test_name = 'Test project'
        test_desc = 'Description for the test project'
        test_pub_view = 'public'
        test_target_date = '2020-04-28'
        test_wiki_category = ''
        r = self.c.post(reverse('project_create'),
                        {'name': test_name,
                         'description': test_desc,
                         'pub_view': test_pub_view,
                         'target_date': test_target_date,
                         'test_wiki_category': test_wiki_category})
        self.assertEqual(r.status_code, 302)
        url = r.url
        r = self.c.get(url)
        self.assertTrue(test_name in r.content)
        self.assertTrue(test_desc in r.content)

    def test_create_project_post_requires_project_name(self):
        r = self.c.post(reverse('project_create'),
                        {'description': 'description',
                         'pub_view': 'public',
                         'target_date': '2020-04-28',
                         'test_wiki_category': ''})
        self.assertEqual(r.status_code, 200)
        self.assertTrue('This field is required.' in r.content)

        r = self.c.post(reverse('project_create'),
                        {'name': '      ',
                         'description': 'description',
                         'pub_view': 'public',
                         'target_date': '2020-04-28',
                         'test_wiki_category': ''})
        self.assertEqual(r.status_code, 200)
        self.assertTrue('This field cannot be blank.' in r.content)

    def test_create_project_post_requires_target_date(self):
        r = self.c.post(reverse('project_create'),
                        {'name': 'Test project name',
                         'description': 'description',
                         'pub_view': 'public',
                         'test_wiki_category': ''})
        self.assertEqual(r.status_code, 200)
        self.assertTrue('This field is required.' in r.content)

    def test_create_project_post_requires_valid_target_date(self):
        r = self.c.post(reverse('project_create'),
                        {'name': 'Test project name',
                         'description': 'description',
                         'pub_view': 'public',
                         'target_date': '2309ur03j30',
                         'test_wiki_category': ''})
        self.assertEqual(r.status_code, 200)
        self.assertTrue('Invalid target date' in r.content)

    def test_create_project_post_private(self):
        self.c.post(reverse('project_create'),
                    {'name': 'Test project name',
                     'description': 'description',
                     'pub_view': 'private',
                     'target_date': '2020-04-28',
                     'test_wiki_category': ''})

    def test_create_project_post_adds_final_release_milestone(self):
        self.c.post(reverse('project_create'),
                    {'name': 'Test project name',
                     'description': 'description',
                     'pub_view': 'public',
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
                     'pub_view': 'public',
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
                     'pub_view': 'public',
                     'target_date': '2020-04-28',
                     'test_wiki_category': ''})
        p = Project.objects.get(name='Test project name')
        self.assertTrue(self.u.userprofile in p.personnel_in_project())

    def test_edit_project_form(self):
        p = ProjectFactory()
        r = self.c.get(p.get_absolute_url() + "edit/")
        self.assertEqual(r.status_code, 200)


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
            reverse('project_detail', args=(p.pid,)) + '?range=300&offset=')
        self.assertEqual(r.status_code, 200)

        r = self.client.get(
            reverse('project_detail', args=(p.pid,)) + '?range=&offset=0')
        self.assertEqual(r.status_code, 200)

        r = self.client.get(
            reverse('project_detail', args=(p.pid,)) + '?range=&offset=')
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
        self.assertTrue(i.get_absolute_url() in r.content)


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

    def test_milestone_page(self):
        m = MilestoneFactory()
        r = self.c.get(m.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(m.name in r.content)

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


class TestItemViews(LoggedInTestMixin, TestCase):
    def setUp(self):
        super(TestItemViews, self).setUp()
        self.c = self.client

    def test_item_view(self):
        i = ItemFactory()
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(i.title in r.content)

    def test_item_view_notification_present(self):
        Flag.objects.create(name='notification_ui', everyone=True)
        i = ItemFactory(assigned_to=self.u.userprofile)
        n = NotifyFactory(item=i, user=self.u)
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue("input_notification" in r.content)
        self.assertTrue(r.context['assigned_to_current_user'])
        self.assertTrue(
            r.context['notifications_enabled_for_current_user'])
        self.assertItemsEqual(r.context['notified_users'], [n])

    def test_item_view_notification_not_present(self):
        Flag.objects.create(name='notification_ui', everyone=True)
        i = ItemFactory()
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue("input_notification" in r.content)
        self.assertFalse(r.context['assigned_to_current_user'])
        self.assertFalse(
            r.context['notifications_enabled_for_current_user'])
        self.assertEqual(len(r.context['notified_users']), 0)

    def test_milestone_view(self):
        i = ItemFactory()
        r = self.c.get(i.milestone.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(i.title in r.content)
        self.assertTrue(i.get_absolute_url() in r.content)

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
        self.assertTrue("<form" in r.content)

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
                "/sign_s3/?s3_object_name=default_name&s3_object_type=foo")
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
        self.assertTrue("tagone" in r.content)
        r = self.c.get("/tag/")
        self.assertTrue("tagone" in r.content)
        r = self.c.get("/tag/tagone/")
        self.assertTrue("tagone" in r.content)
        self.assertTrue(str(i.iid) in r.content)

    def test_remove_tag(self):
        i = ItemFactory()
        r = self.c.post(i.get_absolute_url() + "tag/",
                        dict(tags="tagone, tagtwo"))
        r = self.c.get(i.get_absolute_url() + "remove_tag/tagtwo/")
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue("tagtwo" not in r.content)
        self.assertTrue("tagone" in r.content)


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
        self.assertTrue("this is a comment" in r.content)

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
        self.assertTrue("this is a comment" in r.content)
        self.assertTrue("RESOLVED" in r.content)
        self.assertTrue("FIXED" in r.content)

    def test_resolve_with_time(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "resolve/",
            dict(comment='this is a comment',
                 time='2.5 hours',
                 r_status='FIXED'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue("this is a comment" in r.content)
        self.assertTrue("RESOLVED" in r.content)
        self.assertTrue("FIXED" in r.content)
        self.assertTrue("2:30:00" in r.content)

    def test_resolve_self_assigned(self):
        i = ItemFactory(owner=self.u.userprofile,
                        assigned_to=self.u.userprofile)
        r = self.c.post(
            i.get_absolute_url() + "resolve/",
            dict(comment='this is a comment',
                 r_status='FIXED'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue("this is a comment" in r.content)
        self.assertTrue("VERIFIED" in r.content)

    def test_inprogress(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "inprogress/",
            dict(comment='this is a comment'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue("this is a comment" in r.content)
        self.assertTrue("INPROGRESS" in r.content)

    def test_verify(self):
        i = ItemFactory(status='RESOLVED', r_status='FIXED')
        r = self.c.post(
            i.get_absolute_url() + "verify/",
            dict(comment='this is a comment'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue("this is a comment" in r.content)
        self.assertTrue("VERIFIED" in r.content)

    def test_reopen(self):
        i = ItemFactory(status='RESOLVED', r_status='FIXED')
        r = self.c.post(
            i.get_absolute_url() + "reopen/",
            dict(comment='this is a comment'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue("this is a comment" in r.content)
        self.assertTrue("OPEN" in r.content)

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
        self.assertTrue("VERIFIED" in r.content)
        self.assertTrue("Split" in r.content)
        self.assertTrue("sub item two" in r.content)
        # make sure there are three more items now
        self.assertEqual(Item.objects.all().count(), cnt + 3)

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
        self.assertTrue("this is a todo" in r.content)

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
                 assigned_to=i.assigned_to.username,
                 tags="tagone, tagtwo"))
        r = self.c.get(project.get_absolute_url())
        self.assertTrue("test bug" in r.content)

    def test_add_bug_no_tags(self):
        i = ItemFactory()
        project = i.milestone.project
        r = self.c.post(
            project.get_absolute_url() + "add_bug/",
            dict(title='test bug', description='test',
                 priority='1', milestone=i.milestone.mid,
                 owner=i.owner.username,
                 assigned_to=i.assigned_to.username,
                 tags=""))
        r = self.c.get(project.get_absolute_url())
        self.assertTrue("test bug" in r.content)

    def test_change_priority(self):
        i = ItemFactory()
        r = self.c.get(i.get_absolute_url() + "priority/4/")
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue("CRITICAL" in r.content)

    def test_reassign(self):
        i = ItemFactory()
        u = UserProfileFactory()
        r = self.c.post(i.get_absolute_url() + "assigned_to/",
                        dict(assigned_to=u.username))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue(u.fullname in r.content)

    def test_change_owner(self):
        i = ItemFactory()
        u = UserProfileFactory()
        r = self.c.post(i.get_absolute_url() + "owner/",
                        dict(owner=u.username))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue(u.fullname in r.content)


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
        self.assertTrue(c2.comment in r.content)
        self.assertTrue(c1.comment in r.content)


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
        n.project_id = 0
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
        # see https://pmt.ccnmtl.columbia.edu/item/101115/
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
        StatusUpdateFactory()
        r = self.c.get("/feeds/status/")
        self.assertEquals(r.status_code, 200)

    def test_project_feed(self):
        p = ProjectFactory()
        ItemFactory()
        r = self.c.get("/feeds/project/%s/" % p.pid)
        self.assertEquals(r.status_code, 200)


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
        response = self.client.get(
            reverse('group_detail', args=(self.group.grp.username,)))
        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            self.u.userprofile in response.context['primary_members'])
        self.assertEqual(
            response.context['primary_members'].count(), 1)

        self.assertTrue(
            self.group.username in response.context['other_members'])
        self.assertEqual(
            response.context['other_members'].count(), 1)

        self.assertTrue(
            self.u.userprofile in response.context['eligible_users'])
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
        assigned = ItemFactory(assigned_to=u)
        owned = ItemFactory(owner=u)
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
        self.assertEqual(assigned.assigned_to, self.u.userprofile)

        owned = Item.objects.get(iid=owned.iid)
        self.assertEqual(owned.owner, self.u.userprofile)
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

    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
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

    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
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

    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
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

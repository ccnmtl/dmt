from .factories import (
    ClientFactory, ProjectFactory, MilestoneFactory,
    ItemFactory, NodeFactory, EventFactory, CommentFactory, UserFactory,
    StatusUpdateFactory, NotifyFactory, GroupFactory,
    AttachmentFactory)
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from waffle import Flag
from dmt.claim.models import Claim, PMTUser
from dmt.main.models import (
    Attachment, Comment, Item, ItemClient, Milestone, Project
)
from dmt.main.tests.support.mixins import LoggedInTestMixin
from datetime import timedelta
import json
import unittest


class BasicTest(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

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

    def test_search_empty(self):
        response = self.c.get("/search/?q=")
        self.assertEquals(response.status_code, 200)
        self.assertTrue("alert-error" in response.content)

    def test_dashboard(self):
        response = self.c.get("/dashboard/")
        self.assertEqual(response.status_code, 200)

    def test_owned_items(self):
        response = self.c.get(reverse('owned_items', args=[self.pu.username]))
        self.assertEquals(response.status_code, 200)
        self.assertTrue("Owned Items" in response.content)


class TestClientViews(TestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.client.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

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


class TestProjectViews(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_all_projects_page(self):
        p = ProjectFactory()
        r = self.c.get("/project/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(p.name in r.content)
        self.assertTrue(p.get_absolute_url() in r.content)

    def test_project_page(self):
        p = ProjectFactory()
        r = self.c.get(p.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(p.name in r.content)

    def test_add_node(self):
        p = ProjectFactory()
        r = self.c.post(
            p.get_absolute_url() + "add_node/",
            dict(subject='node subject', body="this is the body"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(p.get_absolute_url())
        self.assertTrue("node subject" in r.content)
        self.assertTrue("this is the body" in r.content)

    def test_add_node_with_tags(self):
        p = ProjectFactory()
        r = self.c.post(
            p.get_absolute_url() + "add_node/",
            dict(subject='node subject', body="this is the body",
                 tags="tagone, tagtwo"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(p.get_absolute_url())
        self.assertTrue("node subject" in r.content)
        self.assertTrue("this is the body" in r.content)

    def test_add_node_empty_body(self):
        p = ProjectFactory()
        r = self.c.post(
            p.get_absolute_url() + "add_node/",
            dict(subject='node subject', body=""))
        self.assertEqual(r.status_code, 302)

    def test_add_status_update(self):
        p = ProjectFactory()
        r = self.c.post(
            p.get_absolute_url() + "add_update/",
            dict(body="xyzzy"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(p.get_absolute_url())
        self.assertTrue("xyzzy" in r.content)

        r = self.c.get(self.pu.get_absolute_url())
        self.assertTrue("xyzzy" in r.content)

        r = self.c.get("/status/")
        self.assertTrue("xyzzy" in r.content)

    def test_add_status_empty_body(self):
        p = ProjectFactory()
        r = self.c.post(
            p.get_absolute_url() + "add_update/",
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
        p = ProjectFactory()
        u = UserFactory()
        p.add_manager(u)
        r = self.c.get(p.get_absolute_url() + "remove_user/%s/" % u.username)
        self.assertTrue(u.fullname in r.content)
        self.assertTrue(u in p.managers())
        self.c.post(p.get_absolute_url() + "remove_user/%s/" % u.username)
        self.assertTrue(u not in p.managers())

    def test_add_user(self):
        p = ProjectFactory()
        u = UserFactory(status='active')
        r = self.c.post(p.get_absolute_url() + "add_user/",
                        dict(username=u.username))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(u in p.all_personnel_in_project())

    def test_add_milestone(self):
        p = ProjectFactory()
        r = self.c.post(p.get_absolute_url() + "add_milestone/",
                        dict(name="NEW TEST MILESTONE",
                             target_date="2020-01-01"))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(p.get_absolute_url())
        self.assertTrue("NEW TEST MILESTONE" in r.content)

    def test_add_action_item_empty_request(self):
        p = ProjectFactory()
        r = self.c.post(p.get_absolute_url() + "add_action_item/",
                        dict())
        self.assertEquals(r.status_code, 404)

    def test_timeline(self):
        p = ProjectFactory()
        r = self.c.get(reverse("project_timeline", args=[p.pid]))
        self.assertEqual(r.status_code, 200)

    def test_add_action_item_form_owner(self):
        milestone = MilestoneFactory()
        milestone.project.add_personnel(self.pu, auth='manager')
        r = self.c.get(milestone.project.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(
            "value=\"testpmtuser\" selected=\"selected\"" in r.content)

    def test_add_action_item(self):
        u = UserFactory()
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
        self.assertEqual(items[0].title, "Untitled")

    def test_add_action_item_empty_title(self):
        u = UserFactory()
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
        self.assertEqual(items[0].title, "Untitled")

    def test_add_action_item_owner(self):
        u = UserFactory()
        milestone = MilestoneFactory()

        r = self.c.post(milestone.project.get_absolute_url() +
                        "add_action_item/",
                        {"assigned_to": u.username,
                         "milestone": milestone.mid,
                         "owner": u.username})
        self.assertEqual(r.status_code, 302)

        items = Item.objects.filter(milestone=milestone, owner=u)
        self.assertEqual(len(items), 1)

    def test_create_project_get(self):
        r = self.c.get(reverse('project_create'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue('Create New Project' in r.content)

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
        self.assertTrue(self.pu in p.personnel_in_project())


class MyProjectViewTests(TestCase):
    def setUp(self):
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.client.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_my_projects_page_in_project(self):
        p = ProjectFactory()
        p.add_personnel(self.pu)
        r = self.client.get(reverse('my_project_list'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(p.name in r.content)
        self.assertTrue(reverse('project_detail', args=(p.pid,)) in r.content)

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
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

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


class TestItemViews(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_item_view(self):
        i = ItemFactory()
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(i.title in r.content)

    def test_item_view_notification_present(self):
        Flag.objects.create(name='notification_ui', everyone=True)
        i = ItemFactory(assigned_to=self.pu)
        NotifyFactory(item=i, username=self.pu)
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue("input_notification" in r.content)
        self.assertTrue(r.context['assigned_to_current_user'])
        self.assertTrue(
            r.context['notifications_enabled_for_current_user'])

    def test_item_view_notification_not_present(self):
        Flag.objects.create(name='notification_ui', everyone=True)
        i = ItemFactory()
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue("input_notification" in r.content)
        self.assertFalse(r.context['assigned_to_current_user'])
        self.assertFalse(
            r.context['notifications_enabled_for_current_user'])

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
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_add_comment(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "comment/",
            dict(comment='this is a comment'))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue("this is a comment" in r.content)

    def test_add_comment_empty(self):
        i = ItemFactory()
        r = self.c.post(
            i.get_absolute_url() + "comment/",
            dict(comment=''))
        self.assertEqual(r.status_code, 302)

    def test_delete_own_comment(self):
        i = ItemFactory()
        e = EventFactory(item=i)
        comment = CommentFactory(item=i, event=e, username=self.u.username)
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
        i = ItemFactory(owner=self.pu, assigned_to=self.pu)
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
        u = UserFactory()
        r = self.c.post(i.get_absolute_url() + "assigned_to/",
                        dict(assigned_to=u.username))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue(u.fullname in r.content)

    def test_change_owner(self):
        i = ItemFactory()
        u = UserFactory()
        r = self.c.post(i.get_absolute_url() + "owner/",
                        dict(owner=u.username))
        self.assertEqual(r.status_code, 302)
        r = self.c.get(i.get_absolute_url())
        self.assertTrue(u.fullname in r.content)


class TestHistory(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

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
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

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


class TestForumTagViews(TestCase):
    def setUp(self):
        self.c = self.client
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

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
        self.u = User.objects.create(username="testuser")
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
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.client.login(username="testuser", password="test")
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

        self.group = GroupFactory()

    def test_group_list(self):
        response = self.client.get(reverse('group_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(self.group) in response.content)

    def test_group_detail(self):
        response = self.client.get(
            reverse('group_detail', args=(self.group.grp.username,)))
        self.assertEqual(response.status_code, 200)
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
        self.assertFalse(user_username in r.content)

    def test_add_user_to_group(self):
        grp_username = self.group.grp.username
        u = UserFactory()
        r = self.client.post(
            reverse('add_user_to_group', args=(grp_username,)),
            dict(username=u.username))
        self.assertEqual(r.status_code, 302)
        r = self.client.get(
            reverse('group_detail', args=(grp_username,)))
        self.assertTrue(u.username in r.content)

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
        self.pu = PMTUser.objects.create(username="testpmtuser",
                                         email="testemail@columbia.edu",
                                         status="active")
        Claim.objects.create(django_user=self.u, pmt_user=self.pu)

    def test_deactivate_user_form(self):
        u = UserFactory(status='active')
        r = self.client.get(u.get_absolute_url() + "deactivate/")
        self.assertEqual(r.status_code, 200)

    def test_deactivate_simple(self):
        u = UserFactory(status='active')
        r = self.client.post(u.get_absolute_url() + "deactivate/",
                             dict())
        self.assertEqual(r.status_code, 302)
        u = PMTUser.objects.get(username=u.username)
        self.assertFalse(u.active())

    def test_deactivate_populated(self):
        u = UserFactory(status='active')
        # this user actually has some stuff
        p = ProjectFactory(caretaker=u)
        assigned = ItemFactory(assigned_to=u)
        owned = ItemFactory(owner=u)
        # reassign it to the request user
        params = dict()
        params["project_%d" % p.pid] = self.pu.username
        params["item_assigned_%d" % assigned.iid] = self.pu.username
        params["item_owner_%d" % owned.iid] = self.pu.username
        r = self.client.post(
            u.get_absolute_url() + "deactivate/",
            params)
        self.assertEqual(r.status_code, 302)
        u = PMTUser.objects.get(username=u.username)
        self.assertFalse(u.active())

        # refetch and check
        p = Project.objects.get(pid=p.pid)
        self.assertEqual(p.caretaker, self.pu)

        assigned = Item.objects.get(iid=assigned.iid)
        self.assertEqual(assigned.assigned_to, self.pu)

        owned = Item.objects.get(iid=owned.iid)
        self.assertEqual(owned.owner, self.pu)


class TestAddTrackersView(LoggedInTestMixin, TestCase):
    def test_add_trackers_view(self):
        r = self.client.get(reverse('add_trackers'))
        self.assertEqual(r.status_code, 200)

    def test_add_trackers_post_empty(self):
        r = self.client.post(reverse('add_trackers'), {})
        self.assertEqual(r.status_code, 302)

    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_add_trackers_post_tracker(self):
        p = ProjectFactory(caretaker=self.pu)
        MilestoneFactory(project=p)
        r = self.client.post(
            reverse('add_trackers'),
            {
                'project-0': p.pid,
                'task-0': 'test',
                'time-0': '1hr',
                'client-uni': ''
            }
        )
        self.assertEqual(r.status_code, 302)

        r = self.client.get(r.url)
        self.assertTrue('Tracker added' in r.content)
        self.assertTrue(p.name in r.content)

        i = Item.objects.last()
        resolve_time = i.get_resolve_time()
        self.assertEqual(resolve_time, timedelta(0, 3600))

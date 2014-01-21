from django.test import TestCase
from .factories import UserFactory, ItemFactory, NodeFactory
from .factories import ProjectFactory, ActualTimeFactory
from datetime import datetime
from dmt.main.models import HistoryItem, ProjectUser


class UserModelTest(TestCase):
    def test_gau(self):
        u = UserFactory()
        self.assertEqual(u.get_absolute_url(), "/user/%s/" % u.username)

    def test_unicode(self):
        u = UserFactory()
        self.assertEqual(str(u), u.fullname)

    def test_active(self):
        u = UserFactory(status='active')
        self.assertTrue(u.active())
        u = UserFactory(status='inactive')
        self.assertFalse(u.active())

    def test_weekly_report(self):
        at = ActualTimeFactory()
        u = at.resolver
        start = datetime(year=2013, month=12, day=16)
        end = datetime(year=2013, month=12, day=23)
        r = u.weekly_report(start, end)
        self.assertEqual(len(r['active_projects']), 1)

    def test_manager_on(self):
        u = UserFactory()
        self.assertEqual(u.manager_on(), [])

    def test_developer_on(self):
        u = UserFactory()
        self.assertEqual(u.developer_on(), [])

    def test_guest_on(self):
        u = UserFactory()
        self.assertEqual(u.guest_on(), [])

    def test_clients_empty(self):
        u = UserFactory()
        self.assertEqual(len(u.clients()), 0)

    def test_user_groups_empty(self):
        u = UserFactory()
        self.assertEqual(len(u.user_groups()), 0)

    def test_users_in_group_empty(self):
        u = UserFactory()
        self.assertEqual(len(u.users_in_group()), 0)

    def test_has_recent_active_projects(self):
        u = UserFactory()
        self.assertFalse(u.has_recent_active_projects())

    def test_recent_active_projects(self):
        u = UserFactory()
        self.assertEqual(u.recent_active_projects(), [])


class ProjectUserTest(TestCase):
    def test_completed_time_for_interval(self):
        u = UserFactory()
        p = ProjectFactory()
        pu = ProjectUser(p, u)
        start = datetime(year=2013, month=12, day=16)
        end = datetime(year=2013, month=12, day=23)
        r = pu.completed_time_for_interval(start, end)
        self.assertEqual(r.total_seconds(), 0.0)


class ItemModelTest(TestCase):
    def test_gau(self):
        i = ItemFactory()
        self.assertEqual(i.get_absolute_url(), "/item/%d/" % i.iid)

    def test_status_class(self):
        i = ItemFactory()
        self.assertEqual(i.status_class(), "open")

    def test_is_bug(self):
        i = ItemFactory()
        self.assertTrue(i.is_bug())

    def test_history(self):
        i = ItemFactory()
        self.assertEqual(i.history(), [])

    def test_priority_label(self):
        i = ItemFactory()
        self.assertEqual(i.priority_label(), 'LOW')

    def test_status_display(self):
        i = ItemFactory()
        self.assertEqual(i.status_display(), 'OPEN')
        i.status = 'RESOLVED'
        i.r_status = 'FIXED'
        self.assertEqual(i.status_display(), 'FIXED')


class HistoryItemTest(TestCase):
    def test_status(self):
        h = HistoryItem()
        self.assertEqual(h.status(), "")


class NodeTest(TestCase):
    def test_get_absolute_url(self):
        n = NodeFactory()
        self.assertEqual(n.get_absolute_url(), "/forum/%d/" % n.nid)

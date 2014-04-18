from django.test import TestCase
from .factories import (
    UserFactory, ItemFactory, NodeFactory, ProjectFactory,
    ActualTimeFactory, MilestoneFactory)
from datetime import datetime, timedelta
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

    def test_total_resolve_times(self):
        u = UserFactory()
        self.assertEqual(u.total_resolve_times(), 0.)

    def test_total_assigned_time(self):
        u = UserFactory()
        self.assertEqual(u.total_assigned_time(), 0.)

    def test_group_fullname(self):
        u = UserFactory(fullname="foo (group)")
        self.assertEqual(u.group_fullname(), "foo")


class ProjectUserTest(TestCase):
    def test_completed_time_for_interval(self):
        u = UserFactory()
        p = ProjectFactory()
        pu = ProjectUser(p, u)
        start = datetime(year=2013, month=12, day=16)
        end = datetime(year=2013, month=12, day=23)
        r = pu.completed_time_for_interval(start, end)
        self.assertEqual(r.total_seconds(), 0.0)


class MilestoneTest(TestCase):
    def test_close_empty_milestone(self):
        m = MilestoneFactory()
        self.assertEqual(m.status, "OPEN")
        m.close_milestone()
        self.assertEqual(m.status, "CLOSED")
        m.close_milestone()
        self.assertEqual(m.status, "CLOSED")

    def test_num_unclosed_items_empty_milestone(self):
        m = MilestoneFactory()
        self.assertEqual(m.num_unclosed_items(), 0)

    def test_should_be_closed_passed_milestone(self):
        m = MilestoneFactory(
            target_date=datetime(year=2000, month=1, day=1).date())
        self.assertTrue(m.should_be_closed())

    def test_update_milestone_passed_milestone(self):
        m = MilestoneFactory(
            target_date=datetime(year=2000, month=1, day=1).date())
        m.update_milestone()
        self.assertEqual(m.status, "CLOSED")


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

    def test_target_date_status(self):
        now = datetime.now()
        i = ItemFactory(target_date=(now + timedelta(days=8)).date())
        self.assertEqual(i.target_date_status(), "ok")

        i = ItemFactory(target_date=(now + timedelta(days=3)).date())
        self.assertEqual(i.target_date_status(), "upcoming")

        i = ItemFactory(target_date=(now).date())
        self.assertEqual(i.target_date_status(), "due")

        i = ItemFactory(target_date=(now - timedelta(days=2)).date())
        self.assertEqual(i.target_date_status(), "overdue")

        i = ItemFactory(target_date=(now - timedelta(days=80)).date())
        self.assertEqual(i.target_date_status(), "late")

    def test_add_project_notification(self):
        i = ItemFactory()
        i.add_project_notification()

    def test_add_cc_inactive_user(self):
        i = ItemFactory()
        u = UserFactory(status='inactive')
        i.add_cc(u)


class HistoryItemTest(TestCase):
    def test_status(self):
        h = HistoryItem()
        self.assertEqual(h.status(), "")


class NodeTest(TestCase):
    def test_get_absolute_url(self):
        n = NodeFactory()
        self.assertEqual(n.get_absolute_url(), "/forum/%d/" % n.nid)

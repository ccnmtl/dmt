from django import forms
from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.utils import timezone
import unittest
from freezegun import freeze_time
from .factories import (
    CommentFactory,
    UserProfileFactory, ItemFactory, NodeFactory, ProjectFactory,
    AttachmentFactory, ClientFactory, StatusUpdateFactory,
    ActualTimeFactory, MilestoneFactory, NotifyFactory,
    GroupFactory)
from datetime import datetime, timedelta
from simpleduration import Duration
from dmt.main.models import (
    ActualTime, Events, InGroup, HistoryItem, Milestone, Notify, ProjectUser,
    truncate_string, HistoryEvent
)


class InGroupTest(TestCase):
    def test_verbose_name(self):
        self.assertEqual(
            InGroup.verbose_name('Test group abc (group)'),
            'Test Group Abc')


class UserModelTest(TestCase):
    def setUp(self):
        self.u = UserProfileFactory()

    def test_gau(self):
        self.assertEqual(
            self.u.get_absolute_url(), "/user/%s/" % self.u.username)

    def test_unicode(self):
        self.assertEqual(str(self.u), self.u.fullname)

    def test_active(self):
        u = UserProfileFactory(status='active')
        self.assertTrue(u.active())
        u = UserProfileFactory(status='inactive')
        self.assertFalse(u.active())

    def test_weekly_report(self):
        at = ActualTimeFactory()
        u = at.user.userprofile
        start = datetime(year=2013, month=12, day=16)
        end = datetime(year=2013, month=12, day=23)
        r = u.weekly_report(start, end)
        self.assertEqual(len(r['active_projects']), 1)

    def test_manager_on(self):
        self.assertEqual(self.u.manager_on(), [])

    def test_developer_on(self):
        self.assertEqual(self.u.developer_on(), [])

    def test_guest_on(self):
        self.assertEqual(self.u.guest_on(), [])

    def test_clients_empty(self):
        self.assertEqual(len(self.u.clients()), 0)

    def test_user_groups_empty(self):
        self.assertEqual(len(self.u.user_groups()), 0)

    def test_user_groups_not_empty(self):
        GroupFactory(username=self.u)
        self.assertEqual(len(self.u.user_groups()), 1)

    def test_users_in_group_empty(self):
        self.assertEqual(len(self.u.users_in_group()), 0)

    def test_has_recent_active_projects(self):
        self.assertFalse(self.u.has_recent_active_projects())

    def test_recent_active_projects(self):
        self.assertEqual(self.u.recent_active_projects(), [])

    def test_total_resolve_times(self):
        self.assertEqual(self.u.total_resolve_times(), 0.)

    def test_total_assigned_time(self):
        self.assertEqual(self.u.total_assigned_time(), 0.)

    def test_group_fullname(self):
        u = UserProfileFactory(fullname="foo (group)")
        self.assertEqual(u.group_fullname(), "foo")

    def test_weekly_report_email_body(self):
        r = self.u.weekly_report_email_body(1.0, True)
        self.assertEqual(
            r,
            """This week you have only logged 1.0 hours.\n\n"""
            """Now is a good time to take care of that.\n""")
        r = self.u.weekly_report_email_body(1.0, False)
        self.assertEqual(
            r,
            """You've logged 1.0 hours this week. Good job!\n""")

    def test_send_weekly_report(self):
        self.u.send_weekly_report()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "PMT Weekly Report")

    def test_timeline_empty(self):
        t = self.u.timeline()
        self.assertEqual(t, [])

    def test_timeline_notempty(self):
        StatusUpdateFactory(user=self.u)
        t = self.u.timeline()
        self.assertEqual(len(t), 1)

    def test_get_absolute_url(self):
        u = UserProfileFactory(grp=False)
        self.assertTrue(u.get_absolute_url().startswith("/user"))

        u = UserProfileFactory(grp=True)
        self.assertTrue(u.get_absolute_url().startswith("/group"))

    def test_progress_report(self):
        d = self.u.progress_report()
        self.assertEqual(d['hours_logged'], 0)
        self.assertEqual(d['week_percentage'], 0)
        self.assertTrue('target_hours' in d)
        self.assertTrue('target_percentage' in d)


class ProjectUserTest(TestCase):
    def test_completed_time_for_interval(self):
        u = UserProfileFactory()
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

    def test_estimated_time_remaining(self):
        m = MilestoneFactory()
        self.assertEqual(m.estimated_time_remaining(), 0.)


class ItemTest(TestCase):
    def test_gau(self):
        i = ItemFactory()
        self.assertEqual(i.get_absolute_url(), "/item/%d/" % i.iid)

    def test_status_class(self):
        i = ItemFactory()
        self.assertEqual(i.status_class(), "dmt-open")

    def test_is_bug(self):
        i = ItemFactory()
        self.assertTrue(i.is_bug())

    def test_history(self):
        i = ItemFactory()
        self.assertEqual(i.history(), [])

    def test_priority_label(self):
        i = ItemFactory()
        self.assertEqual(i.priority_label(), 'LOW')

    def test_resolve(self):
        m = MilestoneFactory()
        p = m.project
        u = UserProfileFactory()
        p.add_item(
            type='action item', title='new item',
            assigned_to=u, owner=u, milestone=m,
            priority=1, description='',
            estimated_time='1hr',
            status='OPEN', r_status='')
        i = m.item_set.first()
        i.resolve(u, 'FIXED', 'test comment')
        self.assertEqual(
            Events.objects.filter(item=i, status='RESOLVED').count(), 1)

    def test_status_display(self):
        i = ItemFactory()
        self.assertEqual(i.status_display(), 'OPEN')
        i.status = 'RESOLVED'
        i.r_status = 'FIXED'
        self.assertEqual(i.status_display(), 'FIXED')

    def test_target_date_status(self):
        now = timezone.now()
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

    def test_add_cc_active_user(self):
        i = ItemFactory()
        u = UserProfileFactory()
        i.add_cc(u)
        self.assertEqual(
            Notify.objects.filter(item=i.iid, username=u.username).count(), 1)

    def test_add_cc_inactive_user(self):
        i = ItemFactory()
        u = UserProfileFactory(status='inactive')
        i.add_cc(u)
        with self.assertRaises(Notify.DoesNotExist):
            Notify.objects.get(item=i.iid, username=u.username)

    def test_add_clients(self):
        i = ItemFactory()
        c = ClientFactory()
        i.add_clients([c])
        self.assertTrue(c in [ic.client for ic in i.itemclient_set.all()])

    def test_copy_clients_to_new_item(self):
        i = ItemFactory()
        c = ClientFactory()
        i.add_clients([c])
        i2 = ItemFactory()
        i.copy_clients_to_new_item(i2)
        self.assertTrue(c in [ic.client for ic in i2.itemclient_set.all()])

    def test_add_resolve_time(self):
        i = ItemFactory()
        u = UserProfileFactory()
        td = Duration('1 hour').timedelta()
        i.add_resolve_time(u, td)
        self.assertEqual(ActualTime.objects.count(), 1)
        actualtime = ActualTime.objects.first()
        self.assertEqual(actualtime.actual_time, timedelta(0, 3600))

    # SQLite can't handle aggregate functions on datetime fields
    # https://docs.djangoproject.com/en/dev/ref/models/querysets/
    # #aggregation-functions
    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_get_resolve_zero(self):
        i = ItemFactory()
        u = UserProfileFactory()
        td = Duration('0h').timedelta()
        i.add_resolve_time(u, td)
        resolve_time = i.get_resolve_time()
        self.assertEqual(resolve_time, timedelta(0, 0))

    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_get_resolve_time_1h(self):
        i = ItemFactory()
        u = UserProfileFactory()
        td = Duration('1 hour').timedelta()
        i.add_resolve_time(u, td)
        resolve_time = i.get_resolve_time()
        self.assertEqual(resolve_time, timedelta(0, 3600))

    def test_reassign(self):
        i = ItemFactory()
        u = UserProfileFactory()
        assignee = UserProfileFactory()
        i.reassign(u, assignee, '')
        self.assertEqual(
            Notify.objects.filter(
                item=i.iid, username=assignee.username).count(), 1)

    @unittest.skipUnless(
        settings.DATABASES['default']['ENGINE'] ==
        'django.db.backends.postgresql_psycopg2',
        "This test requires PostgreSQL")
    def test_get_resolve_time_multiple_times(self):
        i = ItemFactory()

        u = UserProfileFactory()
        td = Duration('1 hour').timedelta()
        i.add_resolve_time(u, td)

        u = UserProfileFactory()
        td = Duration('1 hour').timedelta()
        i.add_resolve_time(u, td)

        resolve_time = i.get_resolve_time()
        self.assertEqual(resolve_time, timedelta(0, 7200))

    def test_update_email(self):
        i = ItemFactory(title="\r\n \r\n linebreaks")
        u2 = UserProfileFactory(status='active')
        NotifyFactory(item=i, username=u2)
        i.update_email("a comment", i.owner)
        self.assertEqual(len(mail.outbox), 1)


class CommentTest(TestCase):
    def setUp(self):
        self.c = CommentFactory()

    def test_is_valid_from_factory(self):
        self.c.full_clean()

    def test_has_been_edited(self):
        self.assertFalse(self.c.has_been_edited())
        with freeze_time('2020-01-01'):
            self.c.comment_src = 'test'
            self.c.comment = 'test'
            self.c.save()
            self.assertTrue(self.c.has_been_edited())


class HistoryItemTest(TestCase):
    def test_status(self):
        h = HistoryItem()
        self.assertEqual(h.status(), "")


class DummyResultSet(object):
    def __init__(self, n):
        self.n = n

    def exists(self):
        return self.n


class DummyQuerySet(object):
    def __init__(self, rs):
        self.rs = rs

    def all(self):
        return self.rs


class DummyEvent(object):
    def __init__(self, qs):
        self.comment_set = qs


def HistoryEventTest(TestCase):
    def test_get_comment_no_result(self):
        rs = DummyResultSet(False)
        qs = DummyQuerySet(rs)
        e = DummyEvent(qs)
        h = HistoryEvent(e)

        self.assertEqual(h._get_comment(), None)


class NodeTest(TestCase):
    def test_get_absolute_url(self):
        n = NodeFactory()
        self.assertEqual(n.get_absolute_url(), "/forum/%d/" % n.nid)

    def test_email_reply_self_reply(self):
        n = NodeFactory()
        n.email_reply("", n.user.userprofile, None)
        # should not send an email when it's a self-reply
        self.assertEqual(len(mail.outbox), 0)

    def test_email_reply_with_project(self):
        n = NodeFactory()
        p = ProjectFactory()
        n.project = p
        u = UserProfileFactory()
        n.save()

        class DummyReply(object):
            subject = "a subject"
        n.email_reply("", u, DummyReply())
        self.assertEqual(len(mail.outbox), 1)

    def test_email_reply_with_bad_header(self):
        n = NodeFactory()
        p = ProjectFactory()
        n.project = p
        u = UserProfileFactory()
        n.save()

        class DummyReply(object):
            subject = "a subject\r\nfoo"
        n.email_reply("", u, DummyReply())
        self.assertEqual(len(mail.outbox), 1)


class ProjectTest(TestCase):
    def test_add_milestone_invalid_target_date(self):
        p = ProjectFactory()
        with self.assertRaises(forms.ValidationError):
            p.add_milestone('name', 'not a date', 'desc')

    def test_add_milestone_valid_target_date(self):
        p = ProjectFactory()
        p.add_milestone('name', '2020-04-04', 'desc')
        p.add_milestone('name', '2020-04-4', 'desc')
        p.add_milestone('name', '2020-4-04', 'desc')
        self.assertEqual(Milestone.objects.filter(project=p).count(), 3)

    def test_managers_empty(self):
        p = ProjectFactory()
        self.assertEqual(p.managers(), [])

    def test_developers_empty(self):
        p = ProjectFactory()
        self.assertEqual(p.developers(), [])

    def test_milestones_empty(self):
        p = ProjectFactory()
        self.assertEqual(len(p.milestones()), 0)

    def test_open_milestones_empty(self):
        p = ProjectFactory()
        self.assertEqual(len(p.open_milestones()), 0)

    def test_open_milestones(self):
        p = ProjectFactory()
        MilestoneFactory(project=p, status='CLOSED')
        self.assertEqual(len(p.milestones()), 1)
        self.assertEqual(len(p.open_milestones()), 0)

    def test_guests_empty(self):
        p = ProjectFactory()
        self.assertEqual(p.guests(), [])

    def test_managers(self):
        p = ProjectFactory()
        u = UserProfileFactory()
        p.add_manager(u)
        self.assertEqual(p.managers(), [u])

    def test_developers(self):
        p = ProjectFactory()
        u = UserProfileFactory()
        p.add_developer(u)
        self.assertEqual(p.developers(), [u])

    def test_guests(self):
        p = ProjectFactory()
        u = UserProfileFactory()
        p.add_guest(u)
        self.assertEqual(p.guests(), [u])

    def test_set_managers(self):
        p = ProjectFactory()
        u1 = UserProfileFactory()
        u2 = UserProfileFactory()
        p.set_managers([u1, u2])
        self.assertEqual(p.managers(), [u1, u2])
        p.set_managers([u1])
        self.assertEqual(p.managers(), [u1])

    def test_set_developers(self):
        p = ProjectFactory()
        u1 = UserProfileFactory()
        u2 = UserProfileFactory()
        p.set_developers([u1, u2])
        self.assertEqual(p.developers(), [u1, u2])
        p.set_developers([u1])
        self.assertEqual(p.developers(), [u1])

    def test_set_guests(self):
        p = ProjectFactory()
        u1 = UserProfileFactory()
        u2 = UserProfileFactory()
        p.set_guests([u1, u2])
        self.assertEqual(p.guests(), [u1, u2])
        p.set_guests([u1])
        self.assertEqual(p.guests(), [u1])

    def test_only_one_role_allowed(self):
        p = ProjectFactory()
        u = UserProfileFactory()
        p.add_manager(u)
        self.assertEqual(p.managers(), [u])
        self.assertEqual(p.developers(), [])
        self.assertEqual(p.guests(), [])
        p.add_developer(u)
        self.assertEqual(p.managers(), [])
        self.assertEqual(p.developers(), [u])
        self.assertEqual(p.guests(), [])
        p.add_guest(u)
        self.assertEqual(p.managers(), [])
        self.assertEqual(p.developers(), [])
        self.assertEqual(p.guests(), [u])

        p.set_managers([u])
        self.assertEqual(p.managers(), [u])
        self.assertEqual(p.developers(), [])
        self.assertEqual(p.guests(), [])
        p.set_developers([u])
        self.assertEqual(p.managers(), [])
        self.assertEqual(p.developers(), [u])
        self.assertEqual(p.guests(), [])
        p.set_guests([u])
        self.assertEqual(p.managers(), [])
        self.assertEqual(p.developers(), [])
        self.assertEqual(p.guests(), [u])

    def test_remove_personnel(self):
        p = ProjectFactory()
        u = UserProfileFactory()
        p.add_manager(u)
        self.assertEqual(p.managers(), [u])
        p.remove_personnel(u)
        self.assertEqual(p.managers(), [])
        self.assertEqual(p.developers(), [])
        self.assertEqual(p.guests(), [])

    def test_all_users_not_in_project(self):
        p = ProjectFactory()
        u1 = UserProfileFactory(status='active')
        u2 = UserProfileFactory(status='active')
        p.add_manager(u1)
        self.assertTrue(u2 in p.all_users_not_in_project())
        self.assertFalse(u1 in p.all_users_not_in_project())

    def test_all_personnel_in_project(self):
        p = ProjectFactory()
        g = GroupFactory()
        p.add_manager(g.grp)
        self.assertTrue(g.username in p.all_personnel_in_project())

    def test_personnel_in_project_sorts_groups_first(self):
        p = ProjectFactory()
        u = UserProfileFactory()
        g = GroupFactory()
        p.add_manager(u)
        p.add_manager(g.grp)
        r = p.personnel_in_project()
        self.assertEqual(r, [g.grp, u])

    def test_add_item_invalid_duration(self):
        m = MilestoneFactory()
        p = m.project
        u = UserProfileFactory()
        p.add_item(type='action item', title="new item",
                   assigned_to=u, owner=u, milestone=m,
                   priority=1, description="",
                   estimated_time="Invalid Estimated Time",
                   status='OPEN', r_status='')
        self.assertTrue(m.item_set.all().count() > 0)
        i = m.item_set.all()[0]
        self.assertEqual(i.estimated_time.seconds, 0)

    def test_add_item_valid_duration_and_timezone(self):
        m = MilestoneFactory()
        p = m.project
        u = UserProfileFactory()
        p.add_item(type='action item', title="new item",
                   assigned_to=u, owner=u, milestone=m,
                   priority=1, description="",
                   estimated_time="2 hours",
                   status='OPEN', r_status='')
        self.assertTrue(m.item_set.all().count() > 0)
        i = m.item_set.all()[0]
        self.assertEqual(i.estimated_time.seconds, 7200)

        # Assert that the last_mod time is within ten mins of what
        # we expect.
        now = timezone.now()
        five_mins = timedelta(minutes=5)
        self.assertTrue(i.last_mod < (now + five_mins))
        self.assertTrue(i.last_mod > (now - five_mins))

    def test_timeline_empty(self):
        p = ProjectFactory()
        self.assertEqual(p.timeline(), [])

    def test_timeline_notempty(self):
        m = MilestoneFactory()
        p = m.project
        u = UserProfileFactory()
        p.add_item(type='action item', title="new item",
                   assigned_to=u, owner=u, milestone=m,
                   priority=1, description="",
                   estimated_time="2 hours",
                   status='OPEN', r_status='')
        t = p.timeline()
        self.assertEqual(len(t), 1)

    def test_email_post(self):
        p = ProjectFactory()
        n = NodeFactory(subject="\r\n \r\n linebreaks", project=p)
        u2 = UserProfileFactory(status='active')
        p.add_manager(u2)
        p.email_post(n, "a body", n.user.userprofile)
        self.assertEqual(len(mail.outbox), 1)


class TestAttachment(TestCase):
    def test_image(self):
        a = AttachmentFactory(type='jpg')
        self.assertTrue(a.image())
        a = AttachmentFactory(type='png')
        self.assertTrue(a.image())
        a = AttachmentFactory(type='gif')
        self.assertTrue(a.image())
        a = AttachmentFactory(type='doc')
        self.assertFalse(a.image())

    def test_get_absolute_url(self):
        a = AttachmentFactory()
        self.assertEqual(a.get_absolute_url(), "/attachment/%d/" % a.id)

    def test_src(self):
        a = AttachmentFactory()
        # not really implemented yet
        self.assertEqual(a.src(), "")


class TestClient(TestCase):
    def test_active(self):
        c = ClientFactory(status='active')
        self.assertTrue(c.active())
        c = ClientFactory(status='inactive')
        self.assertFalse(c.active())


class TestHelpers(unittest.TestCase):
    def test_truncate_string(self):
        self.assertEqual(truncate_string("foobar", length=5), "fooba...")
        self.assertEqual(truncate_string("foobar", length=10), "foobar")

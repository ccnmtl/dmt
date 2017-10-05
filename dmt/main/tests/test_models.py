from django import forms
from django.test import TestCase
from django.core import mail
from django.utils import timezone
from django.utils.timezone import utc
import unittest
from freezegun import freeze_time
from dmt.main.tests.factories import (
    CommentFactory,
    UserProfileFactory, UserFactory, ItemFactory, NodeFactory,
    ProjectFactory, AttachmentFactory, ClientFactory,
    StatusUpdateFactory, ActualTimeFactory, MilestoneFactory,
    NotifyFactory, GroupFactory, ReminderFactory
)
from datetime import datetime, timedelta
from simpleduration import Duration
from dmt.main.utils import simpleduration_string
from dmt.main.models import (
    ActualTime, Events, InGroup, HistoryItem, Milestone, Notify, ProjectUser,
    truncate_string, HistoryEvent, Reminder, Project, WorksOn,
    Comment
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

    def test_make_report_events(self):
        events = self.u._make_report_events(
            Comment.objects.none(),
            ActualTime.objects.none())
        self.assertEqual(len(events), 0)

    def test_report(self):
        at = ActualTimeFactory()
        u = at.user.userprofile
        start = datetime(year=2013, month=12, day=16).replace(tzinfo=utc)
        end = datetime(year=2013, month=12, day=23).replace(tzinfo=utc)
        r = u.report(start, end)
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

    def test_resolved_items_for_interval_empty(self):
        start = datetime(year=2013, month=12, day=16).replace(tzinfo=utc)
        end = datetime(year=2013, month=12, day=23).replace(tzinfo=utc)
        self.assertEqual(
            len(self.u.resolved_items_for_interval(start, end)),
            0)

    def test_resolved_items_for_interval_with_items(self):
        with freeze_time('2013-12-20'):
            ItemFactory()
            ItemFactory()
            i = ItemFactory()
            i.resolve(self.u, 'WORKSFORME', 'resolved')
            i2 = ItemFactory()
            i2.resolve(self.u, 'FIXED', 'done')
            i3 = ItemFactory()
            i3.verify(self.u, 'verified')

            start = datetime(year=2013, month=12, day=16).replace(tzinfo=utc)
            end = datetime(year=2013, month=12, day=23).replace(tzinfo=utc)
            self.assertEqual(
                len(self.u.resolved_items_for_interval(start, end)),
                2)

    def test_resolved_items_for_interval_with_auto_verified(self):
        with freeze_time('2013-12-20'):
            i = ItemFactory()
            i.resolve(self.u, 'WORKSFORME', 'resolved')
            i2 = ItemFactory(owner_user=self.u.user, assigned_user=self.u.user)
            i2.verify(self.u, 'done')
            i3 = ItemFactory()
            i3.verify(self.u, 'verified')

            start = datetime(year=2013, month=12, day=16).replace(tzinfo=utc)
            end = datetime(year=2013, month=12, day=23).replace(tzinfo=utc)

            self.assertEqual(
                len(self.u.resolved_items_for_interval(start, end)),
                2)

    def test_total_resolve_times(self):
        self.assertEqual(self.u.total_resolve_times(), 0.)

    def test_total_assigned_time(self):
        self.assertEqual(self.u.total_assigned_time(), 0.)

    def test_group_fullname(self):
        u = UserProfileFactory(fullname="foo (group)")
        self.assertEqual(u.group_fullname(), "foo")

    def test_weekly_report_email_body(self):
        r = self.u.weekly_report_email_body({
            'resolved_items': 0,
            'hours_logged': 0,
        })
        self.assertEqual(
            r,
            ('Thus far this week, you have resolved 0 item(s) while logging '
             '0.0 hours. Review your weekly report here:\n'
             'https://pmt.ccnmtl.columbia.edu/report/user/{}/weekly'
             '\n\n'
             'Your dashboard shows 0 Outstanding Items. Of these, '
             '0 have a Resolved status and just need your verification '
             'to close the ticket.'
             '\n\n'
             '(PMT Weekly reports end on Sundays at 23:59.)')
            .format(self.u.username)
        )

        r = self.u.weekly_report_email_body({
            'resolved_items': 0,
            'hours_logged': 1,
        })
        self.assertEqual(
            r,
            ('Thus far this week, you have resolved 0 item(s) while logging '
             '1.0 hours. Review your weekly report here:\n'
             'https://pmt.ccnmtl.columbia.edu/report/user/{}/weekly'
             '\n\n'
             'Your dashboard shows 0 Outstanding Items. Of these, '
             '0 have a Resolved status and just need your verification '
             'to close the ticket.'
             '\n\n'
             '(PMT Weekly reports end on Sundays at 23:59.)')
            .format(self.u.username)
        )

    def test_send_weekly_report(self):
        self.u.send_weekly_report()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "PMT Weekly Report")

    def test_send_reminder(self):
        r = ReminderFactory(user=self.u.user)
        self.u.send_reminder(r)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            '[PMT Reminder] {}'.format(r.item.title))

        expected_body = (
            'Reminder: This PMT item is due in {}:\n'.format(
                simpleduration_string(r.reminder_time)) +
            'https://pmt.ccnmtl.columbia.edu{}'.format(
                r.item.get_absolute_url()))

        self.assertEqual(mail.outbox[0].body, expected_body)

    def test_timeline_empty(self):
        t = self.u.timeline()
        self.assertEqual(t, [])

    def test_timeline_notempty(self):
        StatusUpdateFactory(author=self.u.user)
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
        self.assertEqual(d['resolved_items'], 0)

    def test_subscribed_items(self):
        r = self.u.subscribed_items()
        self.assertEqual(len(r), 0)

    def test_get_email(self):
        u = UserProfileFactory(email='')
        u.user.email = "foo@example.com"
        u.user.save()
        self.assertEqual(u.get_email(), u.user.email)

    def test_get_fullname(self):
        u = UserProfileFactory(fullname='')
        self.assertEqual(u.get_fullname(), u.username)

    def test_open_owned_items(self):
        profile = UserProfileFactory()

        # not the owner
        ItemFactory(assigned_user=profile.user)

        # owned but in the Someday/Maybe milestone
        s = MilestoneFactory(name='Someday/Maybe')
        ItemFactory(owner_user=profile.user, milestone=s)

        # owned
        i = ItemFactory(owner_user=profile.user)

        qs = profile.open_owned_items()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), i)


class ProjectUserTest(TestCase):
    def test_completed_time_for_interval(self):
        u = UserProfileFactory()
        p = ProjectFactory()
        pu = ProjectUser(p, u)
        start = datetime(year=2013, month=12, day=16).replace(tzinfo=utc)
        end = datetime(year=2013, month=12, day=23).replace(tzinfo=utc)
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

    def test_active_items(self):
        i = ItemFactory(status='OPEN')
        i2 = ItemFactory(status='INPROGRESS', milestone=i.milestone)
        i3 = ItemFactory(status='RESOLVED', milestone=i.milestone)
        i4 = ItemFactory(status='VERIFIED', milestone=i.milestone)
        r = i.milestone.active_items()
        self.assertIn(i, r)
        self.assertIn(i2, r)
        self.assertIn(i3, r)
        self.assertNotIn(i4, r)

    def test_open_items(self):
        i = ItemFactory(status='OPEN')
        i2 = ItemFactory(status='INPROGRESS', milestone=i.milestone)
        i3 = ItemFactory(status='RESOLVED', milestone=i.milestone)
        i4 = ItemFactory(status='VERIFIED', milestone=i.milestone)
        r = i.milestone.open_items()
        self.assertIn(i, r)
        self.assertNotIn(i2, r)
        self.assertNotIn(i3, r)
        self.assertNotIn(i4, r)

    def test_inprogress_items(self):
        i = ItemFactory(status='OPEN')
        i2 = ItemFactory(status='INPROGRESS', milestone=i.milestone)
        i3 = ItemFactory(status='RESOLVED', milestone=i.milestone)
        i4 = ItemFactory(status='VERIFIED', milestone=i.milestone)
        r = i.milestone.inprogress_items()
        self.assertNotIn(i, r)
        self.assertIn(i2, r)
        self.assertNotIn(i3, r)
        self.assertNotIn(i4, r)

    def test_resolved_items(self):
        i = ItemFactory(status='OPEN')
        i2 = ItemFactory(status='INPROGRESS', milestone=i.milestone)
        i3 = ItemFactory(status='RESOLVED', milestone=i.milestone)
        i4 = ItemFactory(status='VERIFIED', milestone=i.milestone)
        r = i.milestone.resolved_items()
        self.assertNotIn(i, r)
        self.assertNotIn(i2, r)
        self.assertIn(i3, r)
        self.assertNotIn(i4, r)

    def test_verified_items(self):
        i = ItemFactory(status='OPEN')
        i2 = ItemFactory(status='INPROGRESS', milestone=i.milestone)
        i3 = ItemFactory(status='RESOLVED', milestone=i.milestone)
        i4 = ItemFactory(status='VERIFIED', milestone=i.milestone)
        r = i.milestone.verified_items()
        self.assertNotIn(i, r)
        self.assertNotIn(i2, r)
        self.assertNotIn(i3, r)
        self.assertIn(i4, r)


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
            Notify.objects.filter(item=i.iid, user=u.user).count(), 1)

    def test_add_cc_inactive_user(self):
        i = ItemFactory()
        u = UserProfileFactory(status='inactive')
        i.add_cc(u)
        with self.assertRaises(Notify.DoesNotExist):
            Notify.objects.get(item=i.iid, user=u.user)

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

    def test_get_resolve_zero(self):
        i = ItemFactory()
        u = UserProfileFactory()
        td = Duration('0h').timedelta()
        i.add_resolve_time(u, td)
        resolve_time = i.get_resolve_time()
        self.assertEqual(resolve_time, timedelta(0, 0))

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
                item=i.iid, user=assignee.user).count(), 1)

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
        NotifyFactory(item=i, user=u2.user)
        i.update_email("a comment", i.owner_user.userprofile)
        self.assertEqual(len(mail.outbox), 1)

    def test_add_reminder(self):
        i = ItemFactory(title='\r\n \r\n linebreaks')
        u = UserFactory()
        r = i.add_reminder('5d', u)
        self.assertEqual(r.item, i)
        self.assertEqual(r.user, u)
        self.assertEqual(r.reminder_time, timedelta(days=5))


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

    def test_user_accepts_user_or_userprofile(self):
        u = UserFactory()
        self.c.username = u.username
        self.c.save()
        self.assertEqual(self.c.user(), u.userprofile)

        c = CommentFactory()
        up = UserProfileFactory()
        c.username = up.username
        c.save()
        self.assertEqual(c.user(), up)


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
        self.assertEqual(p.managers(), [p.caretaker_user.userprofile])

    def test_ensure_caretaker_in_personnel(self):
        p = ProjectFactory()
        WorksOn.objects.filter(project=p, user=p.caretaker_user).delete()
        self.assertEqual(p.managers(), [])
        p.ensure_caretaker_in_personnel()
        self.assertEqual(p.managers(), [p.caretaker_user.userprofile])

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
        self.assertEqual(set(p.managers()),
                         set([u, p.caretaker_user.userprofile]))

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

    def test_only_one_role_allowed(self):
        p = ProjectFactory()
        u = UserProfileFactory()
        p.add_manager(u)
        self.assertEqual(set(p.managers()),
                         set([u, p.caretaker_user.userprofile]))
        self.assertEqual(p.developers(), [])
        self.assertEqual(p.guests(), [])
        p.add_developer(u)
        self.assertEqual(p.managers(), [p.caretaker_user.userprofile])
        self.assertEqual(p.developers(), [u])
        self.assertEqual(p.guests(), [])
        p.add_guest(u)
        self.assertEqual(p.managers(), [p.caretaker_user.userprofile])
        self.assertEqual(p.developers(), [])
        self.assertEqual(p.guests(), [u])

        p.add_manager(u)
        self.assertEqual(set(p.managers()),
                         set([u, p.caretaker_user.userprofile]))
        self.assertEqual(p.developers(), [])
        self.assertEqual(p.guests(), [])
        p.add_developer(u)
        self.assertEqual(p.managers(), [p.caretaker_user.userprofile])
        self.assertEqual(p.developers(), [u])
        self.assertEqual(p.guests(), [])
        p.add_guest(u)
        self.assertEqual(p.managers(), [p.caretaker_user.userprofile])
        self.assertEqual(p.developers(), [])
        self.assertEqual(p.guests(), [u])

    def test_remove_personnel(self):
        p = ProjectFactory()
        u = UserProfileFactory()
        p.add_manager(u)
        self.assertEqual(set(p.managers()),
                         set([u, p.caretaker_user.userprofile]))
        p.remove_personnel(u)
        self.assertEqual(p.managers(), [p.caretaker_user.userprofile])
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
        self.assertEqual(set(r), set([g.grp, u, p.caretaker_user.userprofile]))

    def test_add_item_created_by(self):
        m = MilestoneFactory()
        p = m.project
        current_user = UserFactory()
        u = UserProfileFactory()
        p.add_item(
            type='action item', title='new item',
            assigned_to=u, owner=u, milestone=m,
            current_user=current_user,
            priority=1, description='',
            estimated_time='2 hours',
            status='OPEN', r_status='')
        self.assertEqual(m.item_set.count(), 1)
        item = m.item_set.first()
        self.assertEqual(item.created_by, current_user)

    def test_add_item_invalid_duration(self):
        m = MilestoneFactory()
        p = m.project
        u = UserProfileFactory()
        p.add_item(type='action item', title="new item",
                   assigned_to=u, owner=u, milestone=m,
                   priority=1, description="",
                   estimated_time="Invalid Estimated Time",
                   status='OPEN', r_status='')
        self.assertTrue(m.item_set.count() > 0)
        i = m.item_set.first()
        self.assertEqual(i.estimated_time.seconds, 0)
        self.assertEqual(Reminder.objects.count(), 0)

    def test_add_item_valid_duration_and_timezone(self):
        m = MilestoneFactory()
        p = m.project
        u = UserProfileFactory()
        p.add_item(type='action item', title="new item",
                   assigned_to=u, owner=u, milestone=m,
                   priority=1, description="",
                   estimated_time="2 hours",
                   status='OPEN', r_status='')
        self.assertTrue(m.item_set.count() > 0)
        i = m.item_set.first()
        self.assertEqual(i.estimated_time.seconds, 7200)

        # Assert that the last_mod time is within ten mins of what
        # we expect.
        now = timezone.now()
        five_mins = timedelta(minutes=5)
        self.assertTrue(i.last_mod < (now + five_mins))
        self.assertTrue(i.last_mod > (now - five_mins))
        self.assertEqual(Reminder.objects.count(), 0)

    def test_add_item_with_reminder(self):
        m = MilestoneFactory()
        p = m.project
        u = UserProfileFactory()
        p.add_item(
            type='action item', title='new item',
            assigned_to=u, owner=u, milestone=m,
            priority=1, description='',
            estimated_time='2 hours',
            status='OPEN', r_status='',
            reminder_duration='7d')
        self.assertEqual(m.item_set.count(), 1)
        self.assertEqual(
            Reminder.objects.count(), 0,
            'add_reminder requires a current_user')

        # Same thing, with a current_user
        i = p.add_item(
            type='action item', title='new item',
            assigned_to=u, owner=u, milestone=m,
            priority=1, description='',
            estimated_time='2 hours',
            status='OPEN', r_status='',
            current_user=u.user,
            reminder_duration='7d')
        self.assertEqual(m.item_set.count(), 2)
        self.assertEqual(Reminder.objects.count(), 1)
        r = Reminder.objects.first()
        self.assertEqual(r.item, i)
        self.assertEqual(r.reminder_time, timedelta(days=7))

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

    @freeze_time('2016-01-04')
    def test_projects_active_between(self):
        now = timezone.now()

        # Make 5 ActualTime objects. This will ultimately create
        # 5 different projects (as well as 5 items, 5 milestones).
        for i in range(5):
            # ActualTime uses "completed" (a DateTimeField) as its
            # primary key, so it must be unique :-/. This will be
            # difficult to change because of this model's foreign
            # key relationships.
            now += timedelta(seconds=10)
            ActualTimeFactory(completed=now)

        # Make one of the projects private
        p = Project.objects.first()
        p.pub_view = False
        p.save()

        start = datetime(year=2016, month=1, day=3).replace(tzinfo=utc)
        end = datetime(year=2016, month=1, day=5).replace(tzinfo=utc)
        projects = Project.projects_active_between(start, end)

        self.assertEqual(projects.count(), 4,
                         'Private projects must be hidden from reports.')

    def test_attachments(self):
        a = AttachmentFactory()
        self.assertEqual(a.item.milestone.project.attachments().count(), 1)


class TestProjectPin(TestCase):
    def test_toggle_pin(self):
        p = ProjectFactory()
        u = UserFactory()

        self.assertEqual(p.projectpin_set.count(), 0)

        p.toggle_pin(u)
        self.assertEqual(p.projectpin_set.count(), 1)

        p.toggle_pin(u)
        self.assertEqual(p.projectpin_set.count(), 0)


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


class TestReminder(TestCase):
    def setUp(self):
        self.r = ReminderFactory()

    def test_is_valid_from_factory(self):
        self.r.full_clean()

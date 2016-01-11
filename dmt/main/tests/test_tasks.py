from django.test import TestCase
from django.utils import timezone
from dmt.main.tests.factories import (
    ItemFactory, MilestoneFactory, ReminderFactory
)
from datetime import timedelta
from dmt.main.models import Milestone, Reminder
from dmt.main.tasks import (
    get_item_counts_by_status, item_counts, hours_logged,
    bump_someday_maybe_target_dates,
    seconds_to_hours, send_reminder_emails
)


class TestHelpers(TestCase):
    def test_get_item_counts_by_status(self):
        d = get_item_counts_by_status()
        self.assertEqual(d['total'], 0)

    def test_item_counts(self):
        d = item_counts()
        self.assertTrue('total_open_items' in d)
        self.assertTrue('estimates_sm' in d)
        self.assertTrue('estimates_non_sm' in d)

    def test_hours_logged(self):
        self.assertEqual(hours_logged(), 0)

    def test_seconds_to_hours(self):
        self.assertEqual(seconds_to_hours(3600), 1.)


class TestBumpSomedayMaybe(TestCase):
    def test_bumper(self):
        m = MilestoneFactory(
            name="Someday/Maybe",
            status="OPEN",
            target_date=timezone.now().date())
        bump_someday_maybe_target_dates()
        m2 = Milestone.objects.get(mid=m.mid)
        self.assertEqual(
            m2.target_date,
            (timezone.now() + timedelta(weeks=52)).date())


class TestReminderTask(TestCase):
    def setUp(self):
        self.r = ReminderFactory()

    def test_task(self):
        send_reminder_emails()
        self.assertEqual(Reminder.objects.count(), 0)

    def test_reminder_email_excludes_closed_items(self):
        resolved_item = ItemFactory(status='RESOLVED')
        ReminderFactory(item=resolved_item)
        verified_item = ItemFactory(status='VERIFIED')
        ReminderFactory(item=verified_item)

        send_reminder_emails()

        self.assertEqual(
            Reminder.objects.filter(item__status='RESOLVED').count(), 1)
        self.assertEqual(
            Reminder.objects.filter(item__status='VERIFIED').count(), 1)

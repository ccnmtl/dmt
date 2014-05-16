from django.test import TestCase
from dmt.main.tasks import (
    get_item_counts_by_status, item_counts, hours_logged,
    seconds_to_hours)


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

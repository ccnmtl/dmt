import unittest
from datetime import timedelta
import dmt.main.utils as utils


class IntervalToHoursTests(unittest.TestCase):
    def test_interval_to_hours(self):
        self.assertEqual(
            utils.interval_to_hours(timedelta(0)),
            0)
        self.assertEqual(
            utils.interval_to_hours(timedelta(hours=1)),
            1)
        self.assertEqual(
            utils.interval_to_hours(timedelta(hours=1, seconds=1800)),
            1.5)
        self.assertEqual(
            utils.interval_to_hours(timedelta(days=1, hours=1, seconds=1800)),
            25.5)


class SafeBasenameTests(unittest.TestCase):
    def test_safe_basename(self):
        self.assertEqual(utils.safe_basename('Foo bar.png'), 'foobar.png')

import unittest
from datetime import timedelta
from dmt.main.utils import (
    interval_to_hours, safe_basename, simpleduration_string
)


class IntervalToHoursTests(unittest.TestCase):
    def test_interval_to_hours(self):
        self.assertEqual(
            interval_to_hours(timedelta(0)),
            0)
        self.assertEqual(
            interval_to_hours(timedelta(hours=1)),
            1)
        self.assertEqual(
            interval_to_hours(timedelta(hours=1, seconds=1800)),
            1.5)
        self.assertEqual(
            interval_to_hours(timedelta(days=1, hours=1, seconds=1800)),
            25.5)


class SafeBasenameTests(unittest.TestCase):
    def test_safe_basename(self):
        self.assertEqual(safe_basename('Foo bar.png'), 'foobar.png')


class SimpleDurationStringTests(unittest.TestCase):
    def test_simpleduration_string(self):
        self.assertEqual(simpleduration_string(timedelta(0)), '')

        self.assertEqual(simpleduration_string(None), '')

        self.assertEqual(
            simpleduration_string(timedelta(days=2)),
            '48h')

        self.assertEqual(
            simpleduration_string(timedelta(days=2, hours=5)),
            '53h')

        self.assertEqual(
            simpleduration_string(timedelta(hours=2)),
            '2h')

        self.assertEqual(
            simpleduration_string(timedelta(hours=2, minutes=30)),
            '2h 30m')

        self.assertEqual(
            simpleduration_string(timedelta(hours=12)),
            '12h')

        self.assertEqual(
            simpleduration_string(timedelta(hours=12, seconds=45)),
            '12h 45s')

        self.assertEqual(
            simpleduration_string(timedelta(hours=1,
                                            minutes=15,
                                            seconds=40)),
            '1h 15m 40s')

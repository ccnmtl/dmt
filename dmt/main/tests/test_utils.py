import unittest
from datetime import timedelta
from dmt.main.utils import (
    new_duration, interval_to_hours, safe_basename, simpleduration_string
)


class NewDurationTests(unittest.TestCase):
    def test_new_duration(self):
        self.assertEqual(
            new_duration('1h').timedelta(),
            timedelta(hours=1))
        self.assertEqual(
            new_duration('30m').timedelta(),
            timedelta(minutes=30))
        self.assertEqual(
            new_duration('24h 15m').timedelta(),
            timedelta(hours=24, minutes=15))

    def test_new_duration_negative(self):
        self.assertEqual(
            new_duration('-1h').timedelta(),
            timedelta(hours=-1))
        self.assertEqual(
            new_duration('-30m').timedelta(),
            timedelta(minutes=-30))
        self.assertEqual(
            new_duration('-60m').timedelta(),
            timedelta(hours=-1))
        self.assertEqual(
            new_duration('-2h 30m').timedelta(),
            timedelta(hours=-2, minutes=-30))


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
        self.assertEqual(simpleduration_string(timedelta(0)), '0h')

        self.assertEqual(simpleduration_string(None), '0h')

        self.assertEqual(
            simpleduration_string(timedelta(days=2)),
            '48h')

        self.assertEqual(
            simpleduration_string(timedelta(minutes=30)),
            '30m')

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

        self.assertEqual(
            simpleduration_string(timedelta(minutes=12, seconds=45)),
            '12m 45s')

    def test_simpleduration_string_negative(self):
        self.assertEqual(simpleduration_string(timedelta(-0)), '0h')

        self.assertEqual(simpleduration_string(None), '0h')

        self.assertEqual(
            simpleduration_string(timedelta(days=-2)),
            '-48h')

        self.assertEqual(
            simpleduration_string(timedelta(minutes=-30)),
            '-30m')

        self.assertEqual(
            simpleduration_string(timedelta(days=-2, hours=-5)),
            '-53h')

        self.assertEqual(
            simpleduration_string(timedelta(hours=-2)),
            '-2h')

        self.assertEqual(
            simpleduration_string(timedelta(hours=-2, minutes=-30)),
            '-2h 30m')

        self.assertEqual(
            simpleduration_string(timedelta(hours=-12)),
            '-12h')

        self.assertEqual(
            simpleduration_string(timedelta(hours=-12, seconds=-45)),
            '-12h 45s')

        self.assertEqual(
            simpleduration_string(timedelta(hours=-1,
                                            minutes=-15,
                                            seconds=-40)),
            '-1h 15m 40s')

        self.assertEqual(
            simpleduration_string(timedelta(minutes=-12, seconds=-45)),
            '-12m 45s')

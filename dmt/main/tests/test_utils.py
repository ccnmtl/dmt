import re
import unittest
from datetime import timedelta
import dmt.main.utils as utils


class CommonMarkRenderTests(unittest.TestCase):
    def test_commonmark_render(self):
        text = 'Paragraph 1\n\n## An h2'
        out = utils.commonmark_render(text)
        pattern = re.compile(r'<p>Paragraph 1\s*</p>\s*<h2>\s*An h2</h2>')
        self.assertTrue(pattern.match(out))

    def test_commonmark_render_empty(self):
        out = utils.commonmark_render('')
        self.assertEqual(out, '')

    def test_commonmark_render_none(self):
        out = utils.commonmark_render(None)
        self.assertEqual(out, '<p>None</p>\n')


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

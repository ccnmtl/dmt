import unittest
import re

from dmt.main.templatetags.dmttags import linkify


class LinkifyTests(unittest.TestCase):
    def test_linkify_random_string(self):
        s = 'abc'
        self.assertEqual(linkify(s), s)

    def test_linkify_html(self):
        s = '<video src="http://example.com"></video>'
        self.assertEqual(linkify(s), s)

    def test_linkify_link(self):
        s = 'Go here: http://columbia.edu'
        self.assertIsNotNone(re.match(
            r'Go here: <a href="http://columbia.edu".*>' +
            r'http://columbia.edu</a>',
            linkify(s)))

    def test_dont_linkify_email(self):
        s = 'email me at user@columbia.edu'
        self.assertEqual(linkify(s), s)

    def test_dont_linkify_pre_blocks(self):
        s = '<pre><iframe src="https://example.com"></iframe></pre>'
        self.assertEqual(linkify(s), s)

    def test_dont_linkify_code_blocks(self):
        s = '<code><iframe src="https://example.com"></iframe></code>'
        self.assertEqual(linkify(s), s)

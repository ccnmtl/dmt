import unittest
from ..utils import safe_basename


class SafeBasenameTests(unittest.TestCase):
    def test_safe_basename(self):
        self.assertEqual(safe_basename('Foo bar.png'), 'foobar.png')

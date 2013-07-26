from django.test import TestCase
from .factories import UserFactory, ItemFactory
from dmt.main.models import HistoryItem


class UserModelTest(TestCase):
    def test_gau(self):
        u = UserFactory()
        self.assertEqual(u.get_absolute_url(), "/user/%s/" % u.username)

    def test_unicode(self):
        u = UserFactory()
        self.assertEqual(str(u), u.fullname)


class ItemModelTest(TestCase):
    def test_gau(self):
        i = ItemFactory()
        self.assertEqual(i.get_absolute_url(), "/item/%d/" % i.iid)

    def test_status_class(self):
        i = ItemFactory()
        self.assertEqual(i.status_class(), "open")

    def test_is_bug(self):
        i = ItemFactory()
        self.assertTrue(i.is_bug())

    def test_history(self):
        i = ItemFactory()
        self.assertEqual(i.history(), [])


class HistoryItemTest(TestCase):
    def test_status(self):
        h = HistoryItem()
        self.assertEqual(h.status(), "")

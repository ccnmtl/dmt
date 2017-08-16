from django.test import TestCase
from .factories import MessageFactory
from ..models import Room


class TestMessage(TestCase):
    def test_unicode(self):
        m = MessageFactory(text="i am the message")
        self.assertTrue("i am the message" in str(m))

    def test_get_absolute_url(self):
        m = MessageFactory()
        self.assertTrue(m.get_absolute_url().startswith("/chat"))


class TestRoom(TestCase):
    def test_recent_messages(self):
        m = MessageFactory()
        r = Room(project=m.project)
        self.assertTrue(m in r.recent_messages())

    def test_unique_dates(self):
        with self.settings(USE_TZ=False):
            m = MessageFactory()
            r = Room(project=m.project)
            self.assertTrue(
                m.added.date() in [d.date() for d in r.unique_dates()])

from django.test import TestCase
from django.test.client import Client
from .factories import ProjectFactory, MilestoneFactory, ItemFactory


class BasicTest(TestCase):
    def setUp(self):
        self.c = Client()

    def test_root(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoketest(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
        assert "PASS" in response.content


class TestProjectViews(TestCase):
    def setUp(self):
        self.c = Client()

    def test_all_projects_page(self):
        p = ProjectFactory()
        r = self.c.get("/project/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(p.name in r.content)
        self.assertTrue(p.get_absolute_url() in r.content)

    def test_project_page(self):
        p = ProjectFactory()
        r = self.c.get(p.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(p.name in r.content)


class TestMilestoneViews(TestCase):
    def setUp(self):
        self.c = Client()

    def test_project_page(self):
        m = MilestoneFactory()
        r = self.c.get(m.project.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(m.name in r.content)
        self.assertTrue(m.get_absolute_url() in r.content)

    def test_milestone_page(self):
        m = MilestoneFactory()
        r = self.c.get(m.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(m.name in r.content)


class TestItemViews(TestCase):
    def setUp(self):
        self.c = Client()

    def test_item_view(self):
        i = ItemFactory()
        r = self.c.get(i.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(i.title in r.content)

    def test_milestone_view(self):
        i = ItemFactory()
        r = self.c.get(i.milestone.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTrue(i.title in r.content)
        self.assertTrue(i.get_absolute_url() in r.content)

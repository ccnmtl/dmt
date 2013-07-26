from django.test import TestCase
from django.test.client import Client
from .factories import ProjectFactory


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

class TestProject(TestCase):
    def setUp(self):
        self.c = Client()

    def test_project_page(self):
        p = ProjectFactory()
        r = self.c.get(p.get_absolute_url())
        self.assertEqual(r.status_code, 200)

from django.test import TestCase
from dmt.main.forms import ProjectPersonnelForm
from dmt.main.tests.factories import (
    UserProfileFactory, ProjectFactory
)


class ProjectPersonnelFormTest(TestCase):
    def test_init(self):
        p = ProjectFactory()
        ProjectPersonnelForm(pid=p.pid)

    def test_personnel_present(self):
        u1 = UserProfileFactory()
        u2 = UserProfileFactory()
        u3 = UserProfileFactory()
        p = ProjectFactory()
        p.add_personnel(u3)
        f = ProjectPersonnelForm(pid=p.pid)

        personnel_in_form = f.fields.get('personnel').queryset.all()
        self.assertTrue(u1 in personnel_in_form)
        self.assertTrue(u2 in personnel_in_form)
        self.assertFalse(u3 in personnel_in_form)

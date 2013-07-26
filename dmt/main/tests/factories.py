import factory
from dmt.main.models import User, Project, Milestone


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    fullname = factory.Sequence(lambda n: 'User {0}'.format(n))
    email = factory.Sequence(lambda n: 'user{0}@columbia.edu'.format(n))
    grp = False
    password = ""


class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project
    pid = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'Test Project {0}'.format(n))
    pub_view = True
    caretaker = factory.SubFactory(UserFactory)


class MilestoneFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Milestone
    mid = factory.Sequence(lambda n: n)
    project = factory.SubFactory(ProjectFactory)

    name = factory.Sequence(lambda n: 'Test Milestone {0}'.format(n))
    target_date = "2020-12-01"
    status = "OPEN"

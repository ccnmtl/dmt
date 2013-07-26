import factory
from dmt.main.models import User, Project


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
    name = "test project"
    pub_view = True
    caretaker = factory.SubFactory(UserFactory)

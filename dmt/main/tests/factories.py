import factory
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.timezone import utc
from dmt.main.models import UserProfile, Project, Milestone, Item
from dmt.main.models import Comment, Events, Node, ActualTime, StatusUpdate
from dmt.main.models import Client, Attachment, Notify, InGroup
from dmt.main.models import create_user_profile


class UserProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserProfile

    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    fullname = factory.Sequence(lambda n: 'User {0}'.format(n))
    email = factory.Sequence(lambda n: 'user{0}@columbia.edu'.format(n))
    grp = False
    status = "active"
    user = factory.SubFactory('dmt.main.tests.factories.UserFactory',
                              userprofile=None)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user_%d" % n)
    userprofile = factory.RelatedFactory(UserProfileFactory, 'user')

    @classmethod
    def _generate(cls, create, attrs):
        post_save.disconnect(create_user_profile, User)
        user = super(UserFactory, cls)._generate(create, attrs)
        post_save.connect(create_user_profile, User)
        return user


class ProjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = Project

    pid = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'Test Project {0}'.format(n))
    pub_view = True
    caretaker_user = factory.SubFactory(UserFactory)


class MilestoneFactory(factory.DjangoModelFactory):
    class Meta:
        model = Milestone

    mid = factory.Sequence(lambda n: n)
    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: 'Test Milestone {0}'.format(n))
    target_date = timezone.now().date() + timedelta(days=3650)
    status = "OPEN"


class ItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = Item

    iid = factory.Sequence(lambda n: n)
    type = "bug"
    owner = factory.SubFactory(UserProfileFactory)
    assigned_to = factory.SubFactory(UserProfileFactory)
    title = factory.Sequence(lambda n: 'Test Item {0}'.format(n))
    milestone = factory.SubFactory(MilestoneFactory)
    status = "OPEN"
    priority = 1


class NotifyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Notify

    item = factory.SubFactory(ItemFactory)
    username = factory.SubFactory(UserProfileFactory)
    user = factory.SubFactory(UserFactory)


class EventFactory(factory.DjangoModelFactory):
    class Meta:
        model = Events

    eid = factory.Sequence(lambda n: n)
    status = "OPEN"
    event_date_time = datetime(2020, 12, 1).replace(tzinfo=utc)
    item = factory.SubFactory(ItemFactory)


class CommentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Comment

    cid = factory.Sequence(lambda n: n)
    comment = "a comment"
    add_date_time = datetime(2020, 12, 1).replace(tzinfo=utc)
    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    item = factory.SubFactory(ItemFactory)
    event = factory.SubFactory(EventFactory)


class NodeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Node

    nid = factory.Sequence(lambda n: n)
    added = datetime(2020, 12, 1).replace(tzinfo=utc)
    modified = datetime(2020, 12, 1).replace(tzinfo=utc)
    user = factory.SubFactory(UserFactory)


class ActualTimeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ActualTime

    item = factory.SubFactory(ItemFactory)
    resolver = factory.SubFactory(UserProfileFactory)
    user = factory.SubFactory(UserFactory)
    actual_time = timedelta(hours=1).total_seconds()
    completed = datetime(2013, 12, 20).replace(tzinfo=utc)


class ClientFactory(factory.DjangoModelFactory):
    class Meta:
        model = Client

    client_id = factory.Sequence(lambda n: n)
    lastname = "clientlastname"
    firstname = "clientfirstname"
    title = "Dr."
    registration_date = datetime(2013, 12, 20).replace(tzinfo=utc)
    department = "Testing"
    school = "TestSchool"
    email = "testclient@columbia.edu"
    contact = factory.SubFactory(UserProfileFactory)
    user = factory.SubFactory(UserFactory)
    status = 'active'


class StatusUpdateFactory(factory.DjangoModelFactory):
    class Meta:
        model = StatusUpdate

    project = factory.SubFactory(ProjectFactory)
    user = factory.SubFactory(UserProfileFactory)
    body = "some text as a body"
    author = factory.SubFactory(UserFactory)


class AttachmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Attachment

    item = factory.SubFactory(ItemFactory)
    filename = "foo.jpg"
    title = "an attachment"
    type = "jpg"
    author = factory.SubFactory(UserProfileFactory)
    user = factory.SubFactory(UserFactory)


class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = InGroup

    grp = factory.SubFactory(UserProfileFactory, grp=True)
    username = factory.SubFactory(UserProfileFactory)

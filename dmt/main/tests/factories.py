from __future__ import unicode_literals

import factory
from factory.django import DjangoModelFactory
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone as django_timezone
from datetime import timezone
from dmt.main.models import (
    UserProfile, Project, Milestone, Item,
    Comment, Events, Node, ActualTime, StatusUpdate,
    Client, Attachment, Notify, InGroup, Reminder
)
from dmt.main.models import create_user_profile


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    fullname = factory.Sequence(lambda n: 'User {0}'.format(n))
    email = factory.Sequence(lambda n: 'user{0}@columbia.edu'.format(n))
    grp = False
    status = "active"
    user = factory.SubFactory('dmt.main.tests.factories.UserFactory',
                              userprofile=None)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user_%d" % n)
    userprofile = factory.RelatedFactory(UserProfileFactory, 'user')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        post_save.disconnect(create_user_profile, User)
        user = super(UserFactory, cls)._create(model_class, *args, **kwargs)
        post_save.connect(create_user_profile, User)
        return user


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    pid = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'Test Project {0}'.format(n))
    pub_view = True
    caretaker_user = factory.SubFactory(UserFactory)
    project_manager_user = factory.SubFactory(UserFactory)


class MilestoneFactory(DjangoModelFactory):
    class Meta:
        model = Milestone

    mid = factory.Sequence(lambda n: n)
    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: 'Test Milestone {0}'.format(n))
    target_date = django_timezone.now().date() + timedelta(days=3650)
    status = "OPEN"


class ItemFactory(DjangoModelFactory):
    class Meta:
        model = Item

    iid = factory.Sequence(lambda n: n)
    type = "bug"
    created_by = factory.SubFactory(UserFactory)
    owner_user = factory.SubFactory(UserFactory)
    assigned_user = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: 'Test Item {0}'.format(n))
    milestone = factory.SubFactory(MilestoneFactory)
    status = "OPEN"
    priority = 1
    target_date = django_timezone.now()


class NotifyFactory(DjangoModelFactory):
    class Meta:
        model = Notify

    item = factory.SubFactory(ItemFactory)
    user = factory.SubFactory(UserFactory)


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Events

    eid = factory.Sequence(lambda n: n)
    status = "OPEN"
    event_date_time = datetime(2020, 12, 1).replace(tzinfo=timezone.utc)
    item = factory.SubFactory(ItemFactory)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    cid = factory.Sequence(lambda n: n)
    comment = "a comment"
    add_date_time = datetime(2020, 12, 1).replace(tzinfo=timezone.utc)
    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    item = factory.SubFactory(ItemFactory)
    event = factory.SubFactory(EventFactory)


class NodeFactory(DjangoModelFactory):
    class Meta:
        model = Node

    nid = factory.Sequence(lambda n: n)
    added = datetime(2020, 12, 1).replace(tzinfo=timezone.utc)
    modified = datetime(2020, 12, 1).replace(tzinfo=timezone.utc)
    user = factory.SubFactory(UserFactory)


class ActualTimeFactory(DjangoModelFactory):
    class Meta:
        model = ActualTime

    item = factory.SubFactory(ItemFactory)
    user = factory.SubFactory(UserFactory)
    actual_time = timedelta(hours=1)
    completed = datetime(2013, 12, 20).replace(tzinfo=timezone.utc)


class ClientFactory(DjangoModelFactory):
    class Meta:
        model = Client

    client_id = factory.Sequence(lambda n: n)
    lastname = "clientlastname"
    firstname = "clientfirstname"
    title = "Dr."
    registration_date = datetime(2013, 12, 20).replace(tzinfo=timezone.utc)
    department = "Testing"
    school = "TestSchool"
    email = "testclient@columbia.edu"
    user = factory.SubFactory(UserFactory)
    status = 'active'


class StatusUpdateFactory(DjangoModelFactory):
    class Meta:
        model = StatusUpdate

    project = factory.SubFactory(ProjectFactory)
    body = "some text as a body"
    author = factory.SubFactory(UserFactory)


class AttachmentFactory(DjangoModelFactory):
    class Meta:
        model = Attachment

    item = factory.SubFactory(ItemFactory)
    filename = "foo.jpg"
    title = "an attachment"
    type = "jpg"
    user = factory.SubFactory(UserFactory)


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = InGroup

    grp = factory.SubFactory(UserProfileFactory, grp=True)
    username = factory.SubFactory(UserProfileFactory)


class ReminderFactory(DjangoModelFactory):
    class Meta:
        model = Reminder

    reminder_time = timedelta(days=1)
    user = factory.SubFactory(UserFactory)
    item = factory.SubFactory(ItemFactory)

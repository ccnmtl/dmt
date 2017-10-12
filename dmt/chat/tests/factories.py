from __future__ import unicode_literals

import factory

from dmt.main.tests.factories import ProjectFactory, UserFactory

from ..models import Message


class MessageFactory(factory.DjangoModelFactory):
    class Meta:
        model = Message
    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)

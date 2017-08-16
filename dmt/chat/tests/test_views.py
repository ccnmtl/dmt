import json

from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from dmt.main.models import Item

from .factories import MessageFactory
from ..views import Chat, FreshToken, ChatPost, ChatArchive, ChatArchiveDate
from ..models import Message


class TestViews(TestCase):
    def test_chat(self):
        m = MessageFactory()
        request = RequestFactory().get(reverse('project-chat',
                                               args=[m.project.pid]))
        request.user = m.user
        response = Chat.as_view()(
            request, pid=m.project.pid)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context_data['project'], m.project)
        self.assertTrue('token' in response.context_data)

    def test_fresh_token(self):
        m = MessageFactory()
        request = RequestFactory().get(reverse('project-chat-fresh-token',
                                               args=[m.project.pid]))
        request.user = m.user
        response = FreshToken.as_view()(
            request, pid=m.project.pid)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('token' in json.loads(response.content))

    def test_chat_post(self):
        m = MessageFactory()
        text = 'new message text'
        request = RequestFactory().post(
            reverse('project-chat-post', args=[m.project.pid]),
            data=dict(text=text))
        request.user = m.user
        response = ChatPost.as_view()(
            request, pid=m.project.pid)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.filter(
            text=text, project=m.project, user=m.user).count(), 1)

    def test_chat_post_add_todo(self):
        m = MessageFactory()
        # the project needs a milestone before
        # we can create a TODO
        m.project.add_milestone('a milestone', '2000-01-01', '')
        text = '/todo new todo from chat'
        request = RequestFactory().post(
            reverse('project-chat-post', args=[m.project.pid]),
            data=dict(text=text))
        request.user = m.user
        response = ChatPost.as_view()(
            request, pid=m.project.pid)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.filter(
            text__startswith='TODO created', project=m.project,
            user=m.user).count(), 1)
        self.assertEqual(Item.objects.filter(
            title='new todo from chat',
            owner_user=m.user, assigned_user=m.user,
        ).count(), 1)

    def test_chat_post_add_tracker(self):
        m = MessageFactory()
        # the project needs a milestone before
        # we can create a tracker
        m.project.add_milestone('a milestone', '2000-01-01', '')
        text = '/tracker new tracker from chat: 2 hours'
        request = RequestFactory().post(
            reverse('project-chat-post', args=[m.project.pid]),
            data=dict(text=text))
        request.user = m.user
        response = ChatPost.as_view()(
            request, pid=m.project.pid)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.filter(
            text__startswith='TRACKER added', project=m.project,
            user=m.user).count(), 1)
        self.assertEqual(Item.objects.filter(
            title='new tracker from chat',
            owner_user=m.user, assigned_user=m.user,
        ).count(), 1)

    def test_archive(self):
        m = MessageFactory()
        request = RequestFactory().get(reverse('project-chat-archive',
                                               args=[m.project.pid]))
        response = ChatArchive.as_view()(
            request, pid=m.project.pid)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context_data['project'], m.project)

    def test_archive_date(self):
        with self.settings(USE_TZ=False):
            m = MessageFactory()
            request = RequestFactory().get(m.get_absolute_url())
            response = ChatArchiveDate.as_view()(
                request, pid=m.project.pid,
                date="{}-{}-{}".format(
                    m.added.year, m.added.month, m.added.day))
            self.assertEqual(response.status_code, 200)

            self.assertEqual(response.context_data['project'], m.project)
            self.assertTrue(m in response.context_data['chat_messages'])

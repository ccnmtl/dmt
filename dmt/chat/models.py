from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

from dmt.main.models import Project


class Room(object):
    """ handy object for chatroom related functionality

    lets us avoid adding these as methods on the
    general `Project` model, keeping all the chat
    specific functionality in here"""

    max_recent_chats = 50

    def __init__(self, project):
        self.project = project

    def recent_messages(self):
        """ just the most recent messages, chronological order

        all chats from the last 24 hours or N, whichever is greater
        """
        now = timezone.now()
        day_ago = now - timedelta(hours=24)

        last_days = set(self.project.message_set.filter(added__gt=day_ago))
        last_n = set(list(self.project.message_set.all()
                          .order_by("-added"))[:self.max_recent_chats])
        messages = last_days.union(last_n)

        messages = sorted(list(messages), key=lambda x: x.added)
        return messages

    def unique_dates(self):
        """ list of dates that this room has messages from """
        return self.project.message_set.datetimes('added', 'day')


class Message(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    text = models.TextField(default=u"", blank=True)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added', ]

    def __unicode__(self):
        return "[%s] %s: %s" % (self.added, self.user.username, self.text)

    def get_absolute_url(self):
        return (reverse('project-chat-archive-date',
                        args=[self.project.pid,
                              "{}-{}-{}".format(
                                  self.added.year,
                                  self.added.month,
                                  self.added.day)])
                + "#message-{}".format(self.pk))

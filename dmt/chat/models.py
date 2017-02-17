from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

from dmt.main.models import Project


class Room(object):
    """ handy object for chatroom related functionality

    lets us avoid adding these as methods on the
    general `Project` model, keeping all the chat
    specific functionality in here"""

    def __init__(self, project):
        self.project = project

    def recent_messages(self):
        """ just the most recent messages, chronological order """
        messages = list(self.project.message_set.all().order_by("-added")[:10])
        messages.reverse()
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

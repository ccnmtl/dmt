from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import (
    Chat, ChatPost, ChatHeartBeat, ChatArchive, ChatArchiveDate, FreshToken)

urlpatterns = [
    url(r'^(?P<pid>\d+)/$',
        login_required(Chat.as_view()),
        name='project-chat'),
    url(r'^(?P<pid>\d+)/fresh_token/$',
        login_required(FreshToken.as_view()),
        name='project-chat-fresh-token'),
    url(r'^(?P<pid>\d+)/post/$',
        login_required(ChatPost.as_view()),
        name='project-chat-post'),
    url(r'^(?P<pid>\d+)/heartbeat/$',
        login_required(ChatHeartBeat.as_view()),
        name='project-chat-heartbeat'),
    url(r'^(?P<pid>\d+)/archive/$',
        login_required(ChatArchive.as_view()),
        name='project-chat-archive'),
    url(r'^(?P<pid>\d+)/archive/(?P<date>\d{4}\-\d+\-\d+)/$',
        login_required(ChatArchiveDate.as_view()),
        name='project-chat-archive-date'),
]

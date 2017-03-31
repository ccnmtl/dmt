import time
import hmac
import hashlib
import json

from datetime import datetime
from random import randint

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView, View

from dmt.main.models import Project
from .models import Room, Message


def gen_token(request, pid):
    username = request.user.username
    sub_prefix = "%s.project_%d" % (settings.ZMQ_APPNAME, int(pid))
    pub_prefix = sub_prefix + "." + username
    now = int(time.mktime(datetime.now().timetuple()))
    salt = randint(0, 2 ** 20)
    ip_address = (request.META.get("HTTP_X_FORWARDED_FOR", "") or
                  request.META.get("REMOTE_ADDR", ""))

    hmc = hmac.new(settings.WINDSOCK_SECRET,
                   '%s:%s:%s:%d:%d:%s' % (username, sub_prefix,
                                          pub_prefix, now, salt,
                                          ip_address),
                   hashlib.sha1).hexdigest()
    return '%s:%s:%s:%d:%d:%s:%s' % (username, sub_prefix,
                                     pub_prefix, now, salt,
                                     ip_address, hmc)


class Chat(TemplateView):
    template_name = "chat/chat.html"

    def get_context_data(self, **kwargs):
        context = super(Chat, self).get_context_data(**kwargs)
        pid = self.kwargs.get('pid', None)
        project = get_object_or_404(Project, pid=pid)
        context['project'] = project
        context['room'] = Room(project=project)
        context['token'] = gen_token(self.request, pid)
        context['websockets_base'] = settings.WINDSOCK_WEBSOCKETS_BASE
        return context


class FreshToken(View):
    def get(self, request, pid):
        project = get_object_or_404(Project, pid=pid)
        return JsonResponse(dict(token=gen_token(request, project.pid)))


class ActionProcessor(object):
    """ process the text

    this is the point where we look for "special" messages
    that represent actions rather than just plain
    text messages. eg, "/todo" or "/tracker"
    actions.

    if none of those appear, we just store the message
    and return the text.

    if there's an action, we do the expected action
    and return the text that should be displayed in
    the channel (eg, "TODO created in project...", etc.)

    this will also be a useful place to hang text transformation
    functions, like replacing "#1234" with a link to the specified
    PMT
    """
    def process(self, text, project, user):
        Message.objects.create(project=project, user=user,
                               text=text)
        return (text, project, user)


class ChatPost(View):
    def post(self, request, pid):
        project = get_object_or_404(Project, pid=pid)
        text = request.POST.get('text', '')
        if text:
            p = ActionProcessor()
            (text, project, user) = p.process(text, project, request.user)
            # send out over zmq

            # the message we are broadcasting
            md = dict(project_pid=project.pid,
                      username=user.username,
                      fullname=user.get_full_name(),
                      userURL=user.userprofile.get_absolute_url(),
                      message_text=text)
            # an envelope that contains that message serialized
            # and the address that we are publishing to
            e = dict(address="%s.project_%d" %
                     (settings.ZMQ_APPNAME, project.pid),
                     content=json.dumps(md))

            broker = settings.BROKER_PROXY()
            broker.send(json.dumps(e))

        return HttpResponseRedirect(reverse('project-chat', args=[pid]))


class ChatHeartBeat(View):
    def post(self, request, pid):
        project = get_object_or_404(Project, pid=pid)
        # # send out over zmq

        # the message we are broadcasting
        md = dict(project_pid=project.pid,
                  username=request.user.username,
                  fullname=request.user.get_full_name(),
                  heartbeat=True)
        # an envelope that contains that message serialized
        # and the address that we are publishing to
        e = dict(address="%s.project_%d" %
                 (settings.ZMQ_APPNAME, project.pid),
                 content=json.dumps(md))

        broker = settings.BROKER_PROXY()
        broker.send(json.dumps(e))
        return HttpResponse("ok")


class ChatArchive(TemplateView):
    template_name = "chat/archive.html"

    def get_context_data(self, **kwargs):
        context = super(ChatArchive, self).get_context_data(**kwargs)
        pid = self.kwargs.get('pid', None)
        project = get_object_or_404(Project, pid=pid)
        context['project'] = project
        context['room'] = Room(project=project)
        return context


class ChatArchiveDate(TemplateView):
    template_name = "chat/archive_date.html"

    def get_context_data(self, **kwargs):
        context = super(ChatArchiveDate, self).get_context_data(**kwargs)
        pid = self.kwargs.get('pid', None)
        date = self.kwargs.get('date', None)
        project = get_object_or_404(Project, pid=pid)
        (year, month, day) = date.split('-')
        d = datetime(year=int(year), month=int(month), day=int(day))
        context['chat_messages'] = project.message_set.filter(
            added__year=year,
            added__month=month,
            added__day=day)
        context['date'] = d
        context['project'] = project
        return context

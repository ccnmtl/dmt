import time
import hmac
import hashlib
import json
import re

from datetime import datetime
from random import randint

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.base import TemplateView, View

from dmt.main.models import Project, Item
from .models import Room, Message


def gen_token(request, pid):
    username = request.user.username
    sub_prefix = "%s.project_%d" % (settings.ZMQ_APPNAME, int(pid))
    pub_prefix = sub_prefix + "." + username
    now = int(time.mktime(timezone.now().timetuple()))
    salt = randint(0, 2 ** 20)  # nosec
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
    def __init__(self, project, user):
        self.project = project
        self.user = user
        # future work: switch these to regexps like
        # django's url router. for now, just simple
        # prefix matching will do...
        self.actions = [
            ('/todo ', self.add_todo),
            ('/tracker ', self.add_tracker),
        ]

        self.filters = [
            self.auto_link_iids,
        ]

    def process(self, text):
        self.text = text
        for prefix, action in self.actions:
            if text.startswith(prefix):
                self.text = action()

        for f in self.filters:
            self.text = f(self.text)

        Message.objects.create(project=self.project, user=self.user,
                               text=self.text)
        return self.text

    def add_todo(self):
        title = self.text[len('/todo '):]
        item = self.project.add_todo(self.user.userprofile, title)
        return "TODO created: [%s](%s)" % (title, item.get_absolute_url())

    def auto_link_iids(self, text):
        """ replace any `#1234` type things with a link to the PMT item """

        """ \B and \b word boundaries are on there to
        avoid detecting, eg, hashes on URLs.

        so in '#123 foo#124 and #125bar' only the '#123' will match
        """
        for iid in re.findall(r'\B\#(\d+)\b', text):
            try:
                item = Item.objects.get(iid=iid)
                title = "#%s: %s" % (iid, item.title)
                url = item.get_absolute_url()
                link = "[%s](%s)" % (title, url)
                text = re.sub(r'\B\#' + iid + r'\b', link, text)
            except Item.DoesNotExist:
                # someone mentioned a non-existant iid
                # just ignore it
                pass
        return text

    def add_tracker(self):
        if ':' not in self.text:
            return self.text
        (title, d) = self.text[len('/tracker '):].split(':')
        item = self.project.add_tracker(self.user, title, d)
        return "TRACKER added: [%s: %s](%s)" % (
            title, d, item.get_absolute_url())


class ChatPost(View):
    def post(self, request, pid):
        project = get_object_or_404(Project, pid=pid)
        text = request.POST.get('text', '')
        if text:
            p = ActionProcessor(project, request.user)
            text = p.process(text)
            # send out over zmq

            # the message we are broadcasting
            md = dict(project_pid=project.pid,
                      username=p.user.username,
                      fullname=p.user.get_full_name(),
                      userURL=p.user.userprofile.get_absolute_url(),
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

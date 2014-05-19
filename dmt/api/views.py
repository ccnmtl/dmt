from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View

from dmt.claim.models import Claim
from dmt.main.models import Project, Item, Client, User

from simpleduration import Duration, InvalidDuration
from json import dumps


class AllProjectsView(View):
    def get(self, request):
        d = [dict(pid=p.pid, value=p.name) for p in Project.objects.all()]
        return HttpResponse(dumps(d))


class AutocompleteProjectView(View):
    def get(self, request):
        d = [dict(pid=p.pid, value=p.name)
             for p in Project.objects.filter(name__icontains=request.GET['q'])]
        return HttpResponse(dumps(d))


class ItemHoursView(View):
    @method_decorator(login_required)
    def post(self, request, pk):
        item = get_object_or_404(Item, iid=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        try:
            d = Duration(request.POST.get('time', "1 hour"))
        except InvalidDuration:
            # eventually, this needs to get back to the user
            # via form validation, but for now
            # we just deal with it...
            d = Duration("0 minutes")

        td = d.timedelta()
        item.add_resolve_time(user, td)
        return HttpResponse("ok")


class GitUpdateView(View):
    def post(self, request):
        iid = request.POST.get('iid', None)
        item = get_object_or_404(Item, iid=iid)
        email = request.POST.get('email', None)
        if '@' not in email:
            email = email + "@columbia.edu"
        user = get_object_or_404(User, email=email)
        status = request.POST.get('status', '')
        resolve_time = request.POST.get('resolve_time', '')
        comment = request.POST.get('comment', '')
        if status == 'FIXED':
            item.status = 'RESOLVED'
            item.r_status = 'FIXED'
            item.add_event("RESOLVED", user, comment)
            item.save()
            item.update_email(
                "%s $%d %s updated\n%s\n" % (
                    item.type, item.iid, item.title, comment),
                user)
        elif comment != "":
            item.add_comment(user, comment)
            item.update_email(
                "comment added to %s $%d %s updated\n%s\n" % (
                    item.type, item.iid, item.title, comment),
                user)
        if resolve_time != "":
            try:
                d = Duration(resolve_time)
                td = d.timedelta()
                item.add_resolve_time(user, td)
            except InvalidDuration:
                # eventually, this needs to get back to the user
                # via form validation, but for now
                # we just deal with it...
                pass
        item.touch()
        return HttpResponse("ok")


class AddTrackerView(View):
    @method_decorator(login_required)
    def post(self, request):
        pid = request.POST.get('pid', None)
        task = request.POST.get('task', None)
        try:
            d = Duration(request.POST.get('time', "1 hour"))
        except InvalidDuration:
            # eventually, this needs to get back to the user
            # via form validation, but for now
            # we just deal with it...
            d = Duration("0 minutes")
        client_uni = request.POST.get('client', '')

        td = d.timedelta()
        # two required fields
        if None in [pid, task]:
            return HttpResponse("bad request")

        project = get_object_or_404(Project, pid=pid)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        milestone = project.upcoming_milestone()
        item = Item.objects.create(
            milestone=milestone,
            type='action item',
            owner=user, assigned_to=user,
            title=task, status='VERIFIED',
            priority=1, target_date=milestone.target_date,
            estimated_time=td)
        if client_uni != '':
            r = Client.objects.filter(
                email=client_uni + "@columbia.edu")
            if r.count() > 0:
                item.add_clients([r[0]])
            else:
                pass
        item.add_resolve_time(user, td)
        return HttpResponse("ok")

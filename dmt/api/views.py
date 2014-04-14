from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View

from dmt.claim.models import Claim
from dmt.main.models import Project, Item, Client

from simpleduration import Duration
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
        d = Duration(request.POST.get('time', "1 hour"))
        td = d.timedelta()
        item.add_resolve_time(user, td)
        return HttpResponse("ok")


class AddTrackerView(View):
    @method_decorator(login_required)
    def post(self, request):
        pid = request.POST.get('pid', None)
        task = request.POST.get('task', None)
        d = Duration(request.POST.get('time', "1 hour"))
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
            try:
                client = Client.objects.get(
                    email=client_uni + "@columbia.edu")
                item.add_clients([client])
            except Client.DoesNotExist:
                pass
        item.add_resolve_time(user, td)
        return HttpResponse("ok")

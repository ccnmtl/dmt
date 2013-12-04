from annoying.decorators import render_to
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from .models import Project, Milestone, Item


@render_to('main/all_projects.html')
def all_projects(request):
    return dict(projects=Project.objects.all())


@render_to('main/project.html')
def project(request, id):
    p = get_object_or_404(Project, pid=id)
    return dict(project=p)


@render_to('main/milestone.html')
def milestone(request, id):
    m = get_object_or_404(Milestone, mid=id)
    return dict(milestone=m)


@render_to('main/item.html')
def item(request, id):
    i = get_object_or_404(Item, iid=id)
    return dict(item=i)

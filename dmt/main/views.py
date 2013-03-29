from annoying.decorators import render_to
from django.shortcuts import get_object_or_404
from .models import Project


@render_to('main/index.html')
def index(request):
    return dict()


@render_to('main/all_projects.html')
def all_projects(request):
    return dict(projects=Project.objects.all())


@render_to('main/project.html')
def project(request, id):
    p = get_object_or_404(Project, pid=id)
    return dict(project=p)

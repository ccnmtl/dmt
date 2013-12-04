from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import Project, Milestone, Item


class AllProjectsView(ListView):
    model = Project
    context_object_name = 'projects'


class ProjectView(DetailView):
    model = Project
    context_object_name = 'project'


class MilestoneView(DetailView):
    model = Milestone
    context_object_name = 'milestone'


class ItemView(DetailView):
    model = Item
    context_object_name = 'item'

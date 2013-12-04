from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import Project, Milestone, Item


class AllProjectsView(ListView):
    model = Project


class ProjectView(DetailView):
    model = Project


class MilestoneView(DetailView):
    model = Milestone


class ItemView(DetailView):
    model = Item

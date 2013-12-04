from annoying.decorators import render_to
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from .models import Project, Milestone, Item


class AllProjectsView(TemplateView):
    template_name = 'main/all_projects.html'

    def get_context_data(self, **kwargs):
        return dict(projects=Project.objects.all())


class ProjectView(DetailView):
    template_name = 'main/project.html'
    model = Project
    context_object_name = 'project'


class MilestoneView(DetailView):
    template_name = 'main/milestone.html'
    model = Milestone
    context_object_name = 'milestone'


class ItemView(DetailView):
    template_name = 'main/item.html'
    model = Item
    context_object_name = 'item'

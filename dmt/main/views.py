from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView, View
from rest_framework import viewsets
import markdown
from .models import Project, Milestone, Item, Node, User, Client
from dmt.claim.models import Claim
from .serializers import (
    UserSerializer, ClientSerializer, ProjectSerializer,
    MilestoneSerializer, ItemSerializer)
from rest_framework import generics


class SearchView(TemplateView):
    template_name = "main/search_results.html"

    def get_context_data(self, **kwargs):
        q = self.request.GET.get('q', '').strip()
        if len(q) < 3:
            return dict(
                error="bad input",
                q=q)
        return dict(
            q=q,
            users=User.objects.filter(
                Q(fullname__icontains=q) |
                Q(bio__icontains=q) |
                Q(username__icontains=q)
            ),
            clients=Client.objects.filter(
                Q(email__icontains=q) |
                Q(firstname__icontains=q) |
                Q(lastname__icontains=q) |
                Q(title__icontains=q) |
                Q(department__icontains=q) |
                Q(school__icontains=q) |
                Q(comments__icontains=q)
            ),
            projects=Project.objects.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            ),
            milestones=Milestone.objects.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            ),
            # TODO: comments/events for items should also be searched
            # and merged in.
            items=Item.objects.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q)
            ),
            nodes=Node.objects.filter(
                Q(body__icontains=q) |
                Q(subject__icontains=q)
            ),
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    paginate_by = 10


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    paginate_by = 20


class ProjectMilestoneList(generics.ListCreateAPIView):
    model = Milestone
    serializer_class = MilestoneSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        return Milestone.objects.filter(project__pk=pk)


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    paginate_by = 20


class MilestoneItemList(generics.ListCreateAPIView):
    model = Item
    serializer_class = ItemSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        return Item.objects.filter(
            milestone__pk=pk).prefetch_related(
            'owner', 'assigned_to',
            'milestone')


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    paginate_by = 20


class AddCommentView(View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        body = request.POST.get('comment', u'')
        if body == '':
            return HttpResponseRedirect(item.get_absolute_url())
        item.add_comment(user, markdown.markdown(body))
        item.touch()
        # TODO: send email
        return HttpResponseRedirect(item.get_absolute_url())

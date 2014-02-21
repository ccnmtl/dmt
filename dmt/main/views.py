from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from rest_framework import viewsets
import markdown
from .models import Project, Milestone, Item, Node, User, Client, ItemClient
from dmt.claim.models import Claim
from .serializers import (
    UserSerializer, ClientSerializer, ProjectSerializer,
    MilestoneSerializer, ItemSerializer)
from rest_framework import generics


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


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


class AddCommentView(LoggedInMixin, View):
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


class ResolveItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        r_status = request.POST.get('r_status', u'FIXED')
        comment = markdown.markdown(request.POST.get('comment', u''))
        if (item.assigned_to.username == item.owner.username and
                item.owner.username == user.username):
            # streamline self-assigned item verification
            item.verify(user, comment)
        else:
            item.resolve(user, r_status, comment)
        item.touch()
        # TODO: send email
        item.milestone.update_milestone()
        return HttpResponseRedirect(item.get_absolute_url())


class InProgressItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        comment = markdown.markdown(request.POST.get('comment', u''))
        item.mark_in_progress(user, comment)
        item.touch()
        # TODO: send email
        item.milestone.update_milestone()
        return HttpResponseRedirect(item.get_absolute_url())


class VerifyItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        comment = markdown.markdown(request.POST.get('comment', u''))
        item.verify(user, comment)
        item.touch()
        # TODO: send email
        item.milestone.update_milestone()
        return HttpResponseRedirect(item.get_absolute_url())


class ReopenItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        comment = markdown.markdown(request.POST.get('comment', u''))
        item.reopen(user, comment)
        item.touch()
        # TODO: send email
        item.milestone.update_milestone()
        return HttpResponseRedirect(item.get_absolute_url())


class SplitItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user

        new_items = []
        for k in request.POST.keys():
            if not k.startswith('title_'):
                continue
            title = request.POST.get(k, False)
            if not title:
                continue
            new_item = Item.objects.create(
                type=item.type,
                owner=item.owner,
                assigned_to=item.assigned_to,
                title=title,
                milestone=item.milestone,
                status='OPEN',
                r_status='',
                description='',
                priority=item.priority,
                target_date=item.target_date,
                estimated_time=item.estimated_time,
                url=item.url)
            new_item.add_event(
                'OPEN',
                user,
                (
                    "<b>%s added</b>"
                    "<p>Split from <a href='%s'>#%d</a></p>" % (
                        item.type, item.get_absolute_url(),
                        item.iid)))
            new_item.touch()
            new_item.setup_default_notification()
            new_item.add_project_notification()
            # TODO: copy tags
            for ic in item.itemclient_set.all():
                ItemClient.objects.create(item=new_item, client=ic.client)
            new_items.append(new_item)
        if len(new_items) > 0:
            comment = (
                "<p>Split into:</p>"
                "<ul>%s</ul>" % "".join(
                    [
                        "<li><a href='%s'>#%d %s</a></li>" % (
                            i.get_absolute_url(),
                            i.iid, i.title) for i in new_items
                    ]))
            item.verify(user, comment)
            item.touch()
        # TODO: send email
        item.milestone.update_milestone()
        return HttpResponseRedirect(item.get_absolute_url())

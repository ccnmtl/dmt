from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.list import ListView
from django_filters.views import FilterView
from django_statsd.clients import statsd
from rest_framework import viewsets
from taggit.models import Tag
from taggit.utils import parse_tags
import markdown
from .models import (
    Project, Milestone, Item, Node, User, Client, ItemClient, StatusUpdate,
    ActualTime)
from .models import interval_sum
from .forms import (
    StatusUpdateForm, NodeUpdateForm, UserUpdateForm, ProjectUpdateForm,
    MilestoneUpdateForm, ItemUpdateForm)
from dmt.claim.models import Claim
from .serializers import (
    UserSerializer, ClientSerializer, ProjectSerializer,
    MilestoneSerializer, ItemSerializer)
from rest_framework import generics
from datetime import datetime, timedelta


def has_claim(user):
    r = Claim.objects.filter(django_user=user)
    return r.count() == 1


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not has_claim(self.request.user):
            return HttpResponseRedirect("/claim/")
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class SearchView(LoggedInMixin, TemplateView):
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
            tags=Tag.objects.filter(name__icontains=q),
            status_updates=StatusUpdate.objects.filter(body__icontains=q),
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
        item.update_email(body, user)
        statsd.incr('main.comment_added')
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
        item.update_email(request.POST.get('comment', u''), user)
        item.milestone.update_milestone()
        statsd.incr('main.resolved')
        return HttpResponseRedirect(item.get_absolute_url())


class InProgressItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        comment = markdown.markdown(request.POST.get('comment', u''))
        item.mark_in_progress(user, comment)
        item.touch()
        item.update_email(request.POST.get('comment', u''), user)
        item.milestone.update_milestone()
        statsd.incr('main.inprogress')
        return HttpResponseRedirect(item.get_absolute_url())


class VerifyItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        comment = markdown.markdown(request.POST.get('comment', u''))
        item.verify(user, comment)
        item.touch()
        item.update_email(request.POST.get('comment', u''), user)
        item.milestone.update_milestone()
        statsd.incr('main.verified')
        return HttpResponseRedirect(item.get_absolute_url())


class ReopenItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        comment = markdown.markdown(request.POST.get('comment', u''))
        item.reopen(user, comment)
        item.touch()
        item.update_email(request.POST.get('comment', u''), user)
        item.milestone.update_milestone()
        statsd.incr('main.reopened')
        return HttpResponseRedirect(item.get_absolute_url())


class ReassignItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        assigned_to = get_object_or_404(
            User,
            username=request.POST.get('assigned_to', ''))
        comment = markdown.markdown(request.POST.get('comment', u''))
        item.reassign(user, assigned_to, comment)
        item.touch()
        item.update_email(request.POST.get('comment', u''), user)
        statsd.incr('main.reassigned')
        return HttpResponseRedirect(item.get_absolute_url())


class ChangeOwnerItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        owner = get_object_or_404(
            User,
            username=request.POST.get('owner', ''))
        comment = markdown.markdown(request.POST.get('comment', u''))
        item.change_owner(user, owner, comment)
        item.touch()
        item.update_email(request.POST.get('comment', u''), user)
        statsd.incr('main.changed_owner')
        return HttpResponseRedirect(item.get_absolute_url())


def clean_tags(s):
    tags = parse_tags(s)
    tags = [t.lower() for t in tags]
    return tags


def tag_object_count(tag):
    """ how many objects total have this tag? """
    return (Item.objects.filter(tags__name__in=[tag.name]).count() +
            Node.objects.filter(tags__name__in=[tag.name]).count())


class TagItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        tags = request.POST.get('tags', u'')
        item.tags.add(*clean_tags(tags))
        item.touch()
        statsd.incr('main.tag_added')
        return HttpResponseRedirect(item.get_absolute_url())


class ItemPriorityView(LoggedInMixin, View):
    def get(self, request, pk, priority):
        # TODO: make this happen through POST
        item = get_object_or_404(Item, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        item.set_priority(int(priority), user)
        item.touch()
        statsd.incr('main.priority_changed')
        return HttpResponseRedirect(item.get_absolute_url())


class RemoveTagFromItemView(LoggedInMixin, View):
    def get(self, request, pk, slug):
        # TODO: make this happen through POST requests
        item = get_object_or_404(Item, pk=pk)
        tag = get_object_or_404(Tag, slug=slug)
        item.tags.remove(tag)
        if tag_object_count(tag) == 0:
            # if you're the last one out, turn off the lights...
            tag.delete()
            statsd.incr('main.tag_deleted')
        item.touch()
        statsd.incr('main.tag_removed')
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
            item.update_email(comment, user)

        item.milestone.update_milestone()
        statsd.incr('main.item_split')
        return HttpResponseRedirect(item.get_absolute_url())


class ItemDetailView(LoggedInMixin, DetailView):
    model = Item


class IndexView(LoggedInMixin, TemplateView):
    template_name = "main/index.html"


class ClientListView(LoggedInMixin, FilterView):
    model = Client
    paginate_by = 100


class StatusUpdateListView(LoggedInMixin, ListView):
    model = StatusUpdate
    paginate_by = 20


class MilestoneListView(LoggedInMixin, ListView):
    model = Milestone
    paginate_by = 50


class StatusUpdateUpdateView(LoggedInMixin, UpdateView):
    model = StatusUpdate
    form_class = StatusUpdateForm


class StatusUpdateDeleteView(LoggedInMixin, DeleteView):
    model = StatusUpdate
    success_url = "/status/"


class ClientDetailView(LoggedInMixin, DetailView):
    model = Client


class ForumView(LoggedInMixin, ListView):
    model = Node
    queryset = Node.objects.filter(reply_to=0)
    paginate_by = 20


class NodeDetailView(LoggedInMixin, DetailView):
    model = Node


class NodeUpdateView(LoggedInMixin, UpdateView):
    model = Node
    form_class = NodeUpdateForm


class NodeDeleteView(LoggedInMixin, DeleteView):
    model = Node
    success_url = "/forum/"


class MilestoneDetailView(LoggedInMixin, DetailView):
    model = Milestone


class ProjectListView(LoggedInMixin, FilterView):
    model = Project


class ProjectDetailView(LoggedInMixin, DetailView):
    model = Project


class ProjectUpdateView(LoggedInMixin, UpdateView):
    model = Project
    form_class = ProjectUpdateForm


class UserListView(LoggedInMixin, FilterView):
    model = User


class UserDetailView(LoggedInMixin, DetailView):
    model = User


class UserUpdateView(LoggedInMixin, UpdateView):
    model = User
    form_class = UserUpdateForm


class MilestoneUpdateView(LoggedInMixin, UpdateView):
    model = Milestone
    form_class = MilestoneUpdateForm


class ItemUpdateView(LoggedInMixin, UpdateView):
    model = Item
    form_class = ItemUpdateForm


class TagListView(LoggedInMixin, ListView):
    model = Tag
    queryset = Tag.objects.all().order_by("name")


class TagDetailView(LoggedInMixin, DetailView):
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagDetailView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.filter(
            tags__name__in=[self.object.name])
        context['nodes'] = Node.objects.filter(
            tags__name__in=[self.object.name])
        return context


class NodeReplyView(LoggedInMixin, View):
    def post(self, request, pk):
        node = get_object_or_404(Node, pk=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        body = request.POST.get('body', u'')
        if body == '':
            return HttpResponseRedirect(node.get_absolute_url())

        node.add_reply(user, body)
        node.touch()
        # TODO: preview mode
        # TODO: tags
        statsd.incr('main.forum_reply')
        return HttpResponseRedirect(node.get_absolute_url())


class ProjectAddTodoView(LoggedInMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pid=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        tags = clean_tags(request.POST.get('tags', u''))
        for k in request.POST.keys():
            if not k.startswith('title_'):
                continue
            title = request.POST.get(k, False)
            if not title:
                continue
            project.add_todo(user, title, tags)
            statsd.incr('main.todo_added')
        return HttpResponseRedirect(project.get_absolute_url())


class ProjectAddItemView(LoggedInMixin, View):
    item_type = "action item"

    def post(self, request, pk):
        project = get_object_or_404(Project, pid=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        title = request.POST.get('title', u"somebody forgot to enter a title")
        tags = clean_tags(request.POST.get('tags', u''))
        description = request.POST.get('description', u'')
        assigned_to = get_object_or_404(
            User, username=request.POST.get('assigned_to'))
        milestone = get_object_or_404(
            Milestone, mid=request.POST.get('milestone'))
        priority = request.POST.get('priority', '1')
        project.add_item(
            type=self.item_type,
            title=title,
            assigned_to=assigned_to,
            owner=user,
            milestone=milestone,
            priority=priority,
            description=description,
            estimated_time=request.POST.get('estimated_time', '1 hour'),
            tags=tags)
        statsd.incr('main.%s_added' % (self.item_type.replace(' ', '_')))
        return HttpResponseRedirect(project.get_absolute_url())


class ProjectAddNodeView(LoggedInMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pid=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        body = request.POST.get('body', u'')
        if body == '':
            return HttpResponseRedirect(project.get_absolute_url())
        tags = clean_tags(request.POST.get('tags', u''))
        project.add_node(request.POST.get('subject', ''), user, body, tags)
        # TODO: preview mode
        statsd.incr('main.forum_post')
        return HttpResponseRedirect(project.get_absolute_url())


class ProjectAddStatusUpdateView(LoggedInMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pid=pk)
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        body = request.POST.get('body', u'')
        if body == '':
            return HttpResponseRedirect(project.get_absolute_url())
        StatusUpdate.objects.create(
            project=project, user=user, body=body)
        statsd.incr('main.status_update')
        return HttpResponseRedirect(project.get_absolute_url())


class TagNodeView(LoggedInMixin, View):
    def post(self, request, pk):
        node = get_object_or_404(Node, pk=pk)
        tags = request.POST.get('tags', u'')
        node.tags.add(*clean_tags(tags))
        node.touch()
        statsd.incr('main.tag_added')
        return HttpResponseRedirect(node.get_absolute_url())


class RemoveTagFromNodeView(LoggedInMixin, View):
    def get(self, request, pk, slug):
        # TODO: make this happen through POST requests
        node = get_object_or_404(Node, pk=pk)
        tag = get_object_or_404(Tag, slug=slug)
        node.tags.remove(tag)
        if tag_object_count(tag) == 0:
            # if you're the last one out, turn off the lights...
            tag.delete()
            statsd.incr('main.tag_deleted')
        node.touch()
        statsd.incr('main.tag_removed')
        return HttpResponseRedirect(node.get_absolute_url())


class DashboardView(LoggedInMixin, TemplateView):
    template_name = "main/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        total_open_items = Item.objects.filter(
            status__in=['OPEN', 'INPROGRESS'])
        open_sm_items = Item.objects.filter(
            status__in=['OPEN', 'INPROGRESS'],
            milestone__name='Someday/Maybe')
        # item counts
        context['total_open_items'] = total_open_items.count()
        context['open_sm_items'] = open_sm_items.count()
        context['open_non_sm_items'] = (
            total_open_items.count() - open_sm_items.count())

        # hour estimates
        total_hours_estimated = interval_sum(
            [i.estimated_time for i in total_open_items]
        ).total_seconds() / 3600.

        sm_hours_estimated = interval_sum(
            [i.estimated_time for i in open_sm_items]
        ).total_seconds() / 3600.

        context['sm_hours_estimated'] = sm_hours_estimated
        context['non_sm_hours_estimated'] = (
            total_hours_estimated - sm_hours_estimated)

        # recent/upcoming milestones
        now = datetime.now()
        four_weeks_ago = now - timedelta(weeks=4)
        four_weeks_future = now + timedelta(weeks=4)
        two_weeks_ago = now - timedelta(weeks=2)

        context['milestones'] = Milestone.objects.filter(
            target_date__gt=four_weeks_ago,
            target_date__lt=four_weeks_future,
            ).order_by("target_date").select_related('project')

        # active projects
        times_logged = ActualTime.objects.filter(
            completed__gt=two_weeks_ago).select_related(
            'item', 'resolver', 'item__milestone',
            'item__milestone__project')
        all_active_items = set([a.item for a in times_logged])
        all_active_projects = set(
            [i.milestone.project for i in all_active_items])
        all_active_users = set([a.resolver for a in times_logged])

        for p in all_active_projects:
            p.recent_hours = interval_sum(
                [a.actual_time for a in times_logged
                 if a.item.milestone.project == p]).total_seconds() / 3600.

        for u in all_active_users:
            u.recent_hours = interval_sum(
                [a.actual_time for a in times_logged
                 if a.resolver == u]).total_seconds() / 3600.

        context['active_projects'] = [
            p for p in sorted(list(all_active_projects),
                              key=lambda x: x.recent_hours,
                              reverse=True)
            if p.recent_hours > 10.]
        context['active_users'] = [
            u for u in sorted(
                list(all_active_users),
                key=lambda x: x.recent_hours,
                reverse=True)
            if u.recent_hours > 10.]

        # week by week breakdown
        week_start = now + timedelta(days=-now.weekday())
        week_end = week_start + timedelta(days=6)

        weeks = [
            (week_start, now),
            (week_start - timedelta(weeks=1), week_end - timedelta(weeks=1)),
            (week_start - timedelta(weeks=2), week_end - timedelta(weeks=2)),
            (week_start - timedelta(weeks=3), week_end - timedelta(weeks=3)),
        ]

        breakdowns = [
            interval_sum(
                [a.actual_time for a in ActualTime.objects.filter(
                    completed__gte=monday,
                    completed__lte=sunday,
                    )]).total_seconds() / 3600.
            for (monday, sunday) in weeks]

        context['breakdowns'] = breakdowns

        context['status_updates'] = StatusUpdate.objects.filter(
            added__gte=two_weeks_ago)
        return context

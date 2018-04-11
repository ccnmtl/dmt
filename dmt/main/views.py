from __future__ import unicode_literals
from urlparse import urljoin
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django_filters.views import FilterView
from django_statsd.clients import statsd
from extra_views import FormSetView, UpdateWithInlinesView
from taggit.models import Tag
from taggit.utils import parse_tags
from dmt.main.mixins import DaterangeMixin
from dmt.main.models import (
    Comment, Project, Milestone, Item, InGroup, Node, UserProfile, Client,
    StatusUpdate, ActualTime, Notify, Attachment, Reminder
)
from dmt.main.models import interval_sum
from dmt.main.filters import ClientFilter, ProjectFilter, UserFilter
from dmt.main.forms import (
    AddTrackerForm, CommentUpdateForm,
    ItemCreateForm, BugCreateForm, ItemUpdateForm,
    RemindersInlineFormSet,
    ProjectCreateForm, StatusUpdateForm, NodeUpdateForm, UserUpdateForm,
    ProjectUpdateForm, MilestoneUpdateForm, ProjectPersonnelForm
)
from dmt.main.templatetags.dmttags import linkify
from .utils import safe_basename, simpleduration_string

from django_markwhat.templatetags.markup import commonmark
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from simpleduration import Duration, InvalidDuration
from s3sign.views import SignS3View as BaseSignS3View
import uuid
import ntpath
import re


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class SuperUserOnlyMixin(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(SuperUserOnlyMixin, self).dispatch(*args, **kwargs)


class SearchView(LoggedInMixin, TemplateView):
    template_name = "main/search_results.html"

    def get_context_data(self, **kwargs):
        q = self.request.GET.get('q', '').strip()
        if len(q) < 3:
            return dict(
                error="bad input",
                q=q)

        item_id = ''
        # Parse the item id if someone searched for, e.g. #9876
        match = re.match(r'^#(\d+)$', q)
        if match:
            item_id = match.groups()[0]

        return dict(
            q=q,
            users=UserProfile.objects.filter(
                Q(fullname__icontains=q) |
                Q(bio__icontains=q) |
                Q(username__icontains=q)
            ),
            projects=Project.objects.filter(
                ~Q(status='Defunct') &
                (
                    Q(name__icontains=q) |
                    Q(description__icontains=q)
                )
            ),
            defunctprojects=Project.objects.filter(
                Q(status='Defunct') &
                (
                    Q(name__icontains=q) |
                    Q(description__icontains=q)
                )
            ),
            milestones=Milestone.objects.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            ),
            # TODO: comments/events for items should also be searched
            # and merged in.
            items=Item.objects.filter(
                ~Q(milestone__project__status='Defunct') &
                (
                    Q(title__icontains=q) |
                    Q(iid__iexact=q) |
                    Q(iid__iexact=item_id) |
                    Q(description__icontains=q)
                )
            ).annotate(
                workedon_total=Sum('actualtime__actual_time')
            ),
            nodes=Node.objects.filter(
                Q(body__icontains=q) |
                Q(subject__icontains=q)
            ),
            tags=Tag.objects.filter(name__icontains=q),
            status_updates=StatusUpdate.objects.filter(body__icontains=q),
        )


def log_time(item, user, request):
    t = request.POST.get('time', False)
    if t:
        try:
            d = Duration(request.POST.get('time', "1 hour"))
            td = d.timedelta()
            item.add_resolve_time(user, td)
        except InvalidDuration:
            pass


class ActualTimeDeleteView(LoggedInMixin, DeleteView):
    model = ActualTime

    def require_owner(self, time):
        """Raise an error if request.user doesn't own the given time."""
        if time.user != self.request.user:
            raise PermissionDenied

    def get_object(self, queryset=None):
        """Ensure that the time is owned by request.user."""
        uuid = self.kwargs['uuid']
        time = ActualTime.objects.get(uuid=uuid)
        self.require_owner(time)
        return time

    def get_success_url(self):
        # Get the item's url from the time
        uuid = self.kwargs['uuid']
        time = get_object_or_404(ActualTime, uuid=uuid)
        return reverse('item_detail', args=(time.item.iid,))

    def post(self, request, *args, **kwargs):
        uuid = self.kwargs['uuid']
        time = get_object_or_404(ActualTime, uuid=uuid)
        self.require_owner(time)
        return super(ActualTimeDeleteView, self).post(request, args, kwargs)


class AddCommentView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = request.user.userprofile
        body = request.POST.get('comment', u'')
        if body == '':
            return HttpResponseRedirect(item.get_absolute_url())

        item.add_comment(user, body, linkify(commonmark(body)))
        item.save()
        item.update_email(body, user)
        log_time(item, user, request)
        statsd.incr('main.comment_added')
        return HttpResponseRedirect(item.get_absolute_url())


class CommentDeleteView(LoggedInMixin, DeleteView):
    model = Comment

    def require_comment_owner(self, comment):
        """Raise an error if request.user doesn't own the given comment."""
        pmt_user = self.request.user.userprofile
        if not comment.user_is_owner(pmt_user):
            raise PermissionDenied

    def get_object(self, queryset=None):
        """Ensure that the comment is owned by request.user."""
        comment = super(CommentDeleteView, self).get_object()
        self.require_comment_owner(comment)
        return comment

    def get_success_url(self):
        # Get the item's url from the comment
        cid = self.kwargs['pk']
        comment = get_object_or_404(Comment, cid=cid)
        item = comment.item
        return reverse('item_detail', args=(item.iid,))

    def post(self, request, *args, **kwargs):
        cid = self.kwargs['pk']
        comment = get_object_or_404(Comment, cid=cid)
        self.require_comment_owner(comment)
        return super(CommentDeleteView, self).post(request, args, kwargs)


class CommentUpdateView(LoggedInMixin, UpdateView):
    model = Comment
    form_class = CommentUpdateForm

    def require_comment_owner(self, comment):
        """Raise an error if request.user doesn't own the given comment."""
        pmt_user = self.request.user.userprofile
        if not comment.user_is_owner(pmt_user):
            raise PermissionDenied

    def get_object(self, queryset=None):
        """Ensure that the comment is owned by request.user."""
        comment = super(CommentUpdateView, self).get_object()
        self.require_comment_owner(comment)
        return comment

    def get_success_url(self):
        # Get the item's url from the comment
        cid = self.kwargs['pk']
        comment = get_object_or_404(Comment, cid=cid)
        item = comment.item
        return reverse('item_detail', args=(item.iid,))


class ResolveItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = request.user.userprofile
        r_status = request.POST.get('r_status', u'FIXED')
        comment = linkify(commonmark(request.POST.get('comment', u'')))
        if (item.assigned_user == item.owner_user and
                item.owner_user == request.user):
            # streamline self-assigned item verification
            item.verify(user, comment)
        else:
            item.resolve(user, r_status, comment)
        item.save()
        item.update_email("Resolved %s\n----\n" % (r_status) +
                          request.POST.get('comment', u''), user)
        item.milestone.update_milestone()
        log_time(item, user, request)
        statsd.incr('main.resolved')
        return HttpResponseRedirect(item.get_absolute_url())


class InProgressItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = request.user.userprofile
        comment = linkify(commonmark(request.POST.get('comment', u'')))
        item.mark_in_progress(user, comment)
        item.save()
        item.update_email("Marked as in-progress\n----\n" +
                          request.POST.get('comment', u''), user)
        item.milestone.update_milestone()
        log_time(item, user, request)
        statsd.incr('main.inprogress')
        return HttpResponseRedirect(item.get_absolute_url())


class VerifyItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = request.user.userprofile
        comment = linkify(commonmark(request.POST.get('comment', u'')))
        item.verify(user, comment)
        item.save()
        item.update_email("Verified\n-----\n" +
                          request.POST.get('comment', u''), user)
        item.milestone.update_milestone()
        log_time(item, user, request)
        statsd.incr('main.verified')
        return HttpResponseRedirect(item.get_absolute_url())


class ReopenItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = request.user.userprofile
        comment = linkify(commonmark(request.POST.get('comment', u'')))
        item.reopen(user, comment)
        item.save()
        item.update_email("Reopened\n-----\n" +
                          request.POST.get('comment', u''), user)
        item.milestone.update_milestone()
        log_time(item, user, request)
        statsd.incr('main.reopened')
        return HttpResponseRedirect(item.get_absolute_url())


class ReassignItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = request.user.userprofile
        assigned_to = get_object_or_404(
            UserProfile,
            username=request.POST.get('assigned_to', ''))
        comment = linkify(commonmark(request.POST.get('comment', u'')))
        item.reassign(user, assigned_to, comment)
        item.save()
        item.update_email("Reassigned\n----\n" +
                          request.POST.get('comment', u''), user)
        log_time(item, user, request)
        statsd.incr('main.reassigned')
        return HttpResponseRedirect(item.get_absolute_url())


class ChangeOwnerItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = request.user.userprofile
        owner = get_object_or_404(
            UserProfile,
            username=request.POST.get('owner', ''))
        comment = linkify(commonmark(request.POST.get('comment', u'')))
        item.change_owner(user, owner, comment)
        item.save()
        item.update_email("Owner changed\n-----\n" +
                          request.POST.get('comment', u''), user)
        log_time(item, user, request)
        statsd.incr('main.changed_owner')
        return HttpResponseRedirect(item.get_absolute_url())


def clean_tags(s):
    tags = parse_tags(s)
    tags = [t.lower() for t in tags]
    return tags


def tag_object_count(tag):
    """ how many objects total have this tag? """
    return tag.taggit_taggeditem_items.all().count()


class TagItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        tags = request.POST.get('tags', u'')
        item.tags.add(*clean_tags(tags))
        item.save()
        statsd.incr('main.tag_added')
        return HttpResponseRedirect(item.get_absolute_url())


class ItemPriorityView(LoggedInMixin, View):
    def get(self, request, pk, priority):
        # TODO: make this happen through POST
        item = get_object_or_404(Item, pk=pk)
        user = request.user.userprofile
        item.set_priority(int(priority), user)
        item.save()
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
        item.save()
        statsd.incr('main.tag_removed')
        return HttpResponseRedirect(item.get_absolute_url())


class SplitItemView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        user = request.user.userprofile

        new_items = []
        titles = [request.POST.get(k) for k in request.POST.keys()
                  if k.startswith('title_') and request.POST.get(k, False)]
        for title in titles:
            new_item = item.clone_to_new_item(title, user)
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
            item.save()
            item.update_email(comment, user)

        item.title = item.title + " (SPLIT)"
        item.save()
        item.milestone.update_milestone()
        statsd.incr('main.item_split')
        return HttpResponseRedirect(item.get_absolute_url())


class ItemDetailView(LoggedInMixin, DetailView):
    model = Item

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)

        context['assigned_to_current_user'] = False
        context['notifications_enabled_for_current_user'] = False
        context['has_reminder'] = False

        current_user = self.request.user

        if (current_user):
            context['assigned_to_current_user'] = \
                (context['item'].assigned_user == current_user)

            try:
                reminder = Reminder.objects.get(
                    user=current_user,
                    item=context['item'])
                context['has_reminder'] = True
                context['reminder_time'] = simpleduration_string(
                    reminder.reminder_time)
            except Reminder.DoesNotExist:
                pass

            all_notifies = Notify.objects.filter(
                item=context['item'].iid).order_by(
                    'user__userprofile__fullname').select_related('user')
            notified_users = [n.user for n in all_notifies]

            context['workedon_total'] = context[
                'object'].actualtime_set.aggregate(total=Sum(
                    'actual_time'))['total']

            current_user_notification = all_notifies.filter(
                user=current_user).first()

            context['notifications_enabled_for_current_user'] = \
                True if current_user_notification else False

            context['notified_users'] = notified_users

            all_personnel = \
                context['object'].milestone.project.all_personnel_in_project()
            context['all_personnel'] = all_personnel
            context['potential_subscribers'] = [
                u.user for u in all_personnel if u.user not in notified_users]

        iid = context['object'].iid
        context['clients'] = Client.objects.filter(
            itemclient__item=iid).order_by('lastname')
        context['times'] = context['object'].actualtime_set.order_by(
            'completed')

        return context


class ItemAddSubscriberView(LoggedInMixin, View):
    success_message = '<strong>%s</strong> has been subscribed to this item.'

    def post(self, request, pk):
        subscriber = self.request.POST.get('subscriber')
        if not subscriber:
            messages.error(self.request, 'No subscriber provided.')
            return HttpResponseRedirect(reverse('item_detail', args=[pk]))

        subscriber = get_object_or_404(User, username=subscriber)
        item = get_object_or_404(Item, pk=pk)

        if Notify.objects.filter(user=subscriber, item=item).exists():
            # already an entry
            return HttpResponseRedirect(reverse('item_detail', args=[pk]))

        Notify.objects.create(user=subscriber, item=item)

        messages.success(
            self.request,
            mark_safe(self.success_message % subscriber.userprofile))  # nosec

        if request.user != subscriber:
            item.send_new_subscriber_mail(request.user, subscriber)

        return HttpResponseRedirect(reverse('item_detail', args=[pk]))


class IndexView(LoggedInMixin, TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        if self.request.user:
            context['subscribed_items'] = \
                self.request.user.userprofile.subscribed_items()
        return context


class ClientListView(LoggedInMixin, FilterView):
    filterset_class = ClientFilter
    model = Client
    paginate_by = 100


class AddClientView(LoggedInMixin, CreateView):
    model = Client
    fields = ['email', 'lastname', 'firstname', 'department', 'school']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'active'
        form.instance.save()
        return super(AddClientView, self).form_valid(form)


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


class DeleteTagView(LoggedInMixin, DeleteView):
    model = Tag
    success_url = "/tag/"


class MergeTagView(LoggedInMixin, View):
    template_name = "main/merge_tag_form.html"

    def get(self, request, slug):
        tag = get_object_or_404(Tag, slug=slug)
        all_tags = Tag.objects.all().order_by('name')
        return render(request, self.template_name,
                      dict(tag=tag, all_tags=all_tags))

    def post(self, request, slug):
        t = get_object_or_404(Tag, slug=slug)
        t2 = get_object_or_404(Tag, slug=request.POST.get('tag'))

        # see note in TagDetailView on why this iteration is weird:
        items = [ti.content_object
                 for ti
                 in t.taggit_taggeditem_items.all()
                 if ti.content_object.__class__ == Item]
        nodes = [ti.content_object
                 for ti
                 in t.taggit_taggeditem_items.all()
                 if ti.content_object.__class__ == Node]
        for o in items + nodes:
            o.tags.remove(t)
            o.tags.add(t2)
        t.delete()
        return HttpResponseRedirect(reverse('tag_detail', args=[t2.slug]))


class ClientDetailView(LoggedInMixin, DetailView):
    model = Client

    def get_context_data(self, **kwargs):
        context = super(ClientDetailView, self).get_context_data(**kwargs)

        items = Item.objects.select_related() \
            .filter(itemclient__client_id__exact=context['object'].client_id) \
            .order_by('-last_mod')[:15]
        context['recent_items'] = items
        return context


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

    def move_items(self, request, items, new_milestone):
        item_names = []

        for pk in items:
            item = get_object_or_404(Item, iid=pk)
            item.milestone = new_milestone
            item.save()
            item_names.append(
                '<a href="{}">{}</a>'.format(
                    item.get_absolute_url(), item.title))

        # Update the milestone's status, because it might be empty
        # now.
        milestone = self.get_object()
        milestone.update_milestone()

        if len(item_names) > 0:
            msg = 'Moved the following items to ' + \
                  '<strong>{}</strong>: {}'.format(
                      new_milestone.name,
                      ', '.join(item_names))
            messages.success(request, mark_safe(msg))  # nosec

    @staticmethod
    def reassign_items(request, items, new_assignee):
        item_names = []
        for pk in items:
            item = get_object_or_404(Item, iid=pk)
            item.reassign(request.user.userprofile, new_assignee, '')
            item_names.append(
                '<a href="{}">{}</a>'.format(
                    item.get_absolute_url(), item.title))

        if len(item_names) > 0:
            msg = 'Assigned the following items to ' + \
                  '<strong>{}</strong>: {}'.format(
                      new_assignee.get_fullname(),
                      ', '.join(item_names))
            messages.success(request, mark_safe(msg))  # nosec

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        items = request.POST.getlist('_selected_action')

        if action == 'move' and request.POST.get('move_to'):
            milestone_id = request.POST.get('move_to')
            milestone = get_object_or_404(Milestone, mid=milestone_id)
            self.move_items(request, items, milestone)
        elif action == 'assign' and request.POST.get('assigned_to'):
            assign_to = request.POST.get('assigned_to')
            assignee = get_object_or_404(UserProfile, username=assign_to)
            self.reassign_items(request, items, assignee)

        return HttpResponseRedirect(
            reverse('milestone_detail', args=args, kwargs=kwargs))


class GroupCreateView(LoggedInMixin, View):
    def post(self, request):
        group_name = request.POST.get('group')
        username = "grp_" + re.sub(r'\W', '', group_name).lower()
        if not group_name or UserProfile.objects.filter(
                username=username).exists():
            return HttpResponseRedirect(reverse('group_list'))
        # we need a 1-1 mapping to a django user
        user = User.objects.create(
            username=username,
            first_name=group_name,
            last_name='(group)',
            is_superuser=False,
            is_staff=False,
            is_active=True,
            email='nobody@localhost',
        )
        user.set_unusable_password()
        group_name = group_name + " (group)"
        up = user.userprofile
        up.fullname = group_name
        up.email = 'nobody@localhost'
        up.grp = True
        up.save()
        return HttpResponseRedirect(
            reverse('group_detail', args=(username,)))


class ProjectCreateView(LoggedInMixin, CreateView):
    model = Project
    form_class = ProjectCreateForm

    def form_valid(self, form):
        form.instance.caretaker_user = self.request.user
        form.instance.save()

        try:
            # Add Final Release milestone
            form.instance.add_milestone(
                'Final Release',
                form.data['target_date'],
                'project completion')

            # Add Someday/Maybe milestone, with a due date 2 years
            # after the target date of the project.
            target_date = parse_date(form.data['target_date'])
            milestone_due_date = target_date + relativedelta(years=2)
            form.instance.add_milestone(
                'Someday/Maybe',
                milestone_due_date.strftime('%Y-%m-%d'),
                'A milestone for items that will ' +
                'not be immediately worked on. ' +
                'Items in this milestone will not ' +
                'appear on a homepage or in time ' +
                'estimates.')
            return super(ProjectCreateView, self).form_valid(form)
        except forms.ValidationError, e:
            form.errors['target_date'] = [e.message]
            return super(ProjectCreateView, self).form_invalid(form)


class ProjectListView(LoggedInMixin, FilterView):
    filterset_class = ProjectFilter
    model = Project


class MyProjectListView(LoggedInMixin, ListView):
    model = Project
    template_name = 'main/my_projects.html'

    def get_queryset(self):
        current_user = self.request.user.userprofile
        project_list = current_user.personnel_on()
        return project_list


class ProjectDetailView(LoggedInMixin, DaterangeMixin, DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        ctx = super(ProjectDetailView, self).get_context_data(**kwargs)
        unverified_items = Item.objects.filter(
            milestone__project=self.object).filter(
                ~Q(status='VERIFIED')
        ).select_related('milestone')
        m_set = set([i.milestone for i in unverified_items])
        ctx['milestones'] = [
            m for m in self.object.milestones()
            if m in m_set]
        ctx['users_active_in_range'] = ctx['object'].users_active_between(
            self.interval_start, self.interval_end)
        ctx['estimated_time_report'] = \
            ctx['object'].user_estimated_time_report()
        ctx['total_hours'] = round(
            sum([u.hours_logged.total_seconds()
                 for u in ctx['users_active_in_range']]) / 3600, 2)
        ctx['personnel_form'] = ProjectPersonnelForm(
            pid=ctx['object'].pid)
        ctx['pinned'] = self.object.projectpin_set.filter(
            user=self.request.user).exists()
        return ctx


class ProjectPinView(LoggedInMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project.toggle_pin(request.user)
        return HttpResponseRedirect(reverse('project_detail', args=(pk,)))


class ProjectTimeLineView(LoggedInMixin, DaterangeMixin, DetailView):
    model = Project
    template_name = "main/project_timeline.html"

    def get_context_data(self, **kwargs):
        # Set the default interval to one week instead of one month.
        self.delta = timedelta(weeks=1)
        ctx = super(ProjectTimeLineView, self).get_context_data(**kwargs)

        ctx['timeline'] = self.object.timeline(
            start=self.interval_start,
            end=self.interval_end,
        )
        return ctx


class UserTimeLineView(LoggedInMixin, DaterangeMixin, DetailView):
    model = UserProfile
    template_name = "main/user_timeline.html"

    def get_context_data(self, **kwargs):
        # Set the default interval to one week instead of one month.
        self.delta = timedelta(weeks=1)
        ctx = super(UserTimeLineView, self).get_context_data(**kwargs)

        ctx['timeline'] = self.object.timeline(
            start=self.interval_start,
            end=self.interval_end,
        )
        return ctx


class ProjectUpdateView(LoggedInMixin, UpdateView):
    model = Project
    form_class = ProjectUpdateForm
    template_name_suffix = '_update_form'


class UserListView(LoggedInMixin, FilterView):
    template_name = 'main/user_filter.html'
    filterset_class = UserFilter
    model = UserProfile

    def get_queryset(self):
        user_list = UserProfile.objects.filter(grp__exact=False)
        return user_list


class UserDetailView(LoggedInMixin, DetailView):
    model = UserProfile
    template_name = "main/user_detail.html"


class OwnedItemsView(LoggedInMixin, DetailView):
    model = UserProfile
    template_name = "main/owned_items.html"


class UserUpdateView(LoggedInMixin, UpdateView):
    template_name = 'main/user_form.html'
    model = UserProfile
    form_class = UserUpdateForm


class DeactivateUserView(SuperUserOnlyMixin, View):
    template_name = "main/user_deactivate.html"

    def get(self, request, pk):
        u = get_object_or_404(UserProfile, username=pk)
        return render(request, self.template_name,
                      dict(user=u))

    def post(self, request, pk):
        u = get_object_or_404(UserProfile, username=pk)
        u.status = 'inactive'
        u.save()
        for k in request.POST.keys():
            if k.startswith('project_'):
                pid = k[len('project_'):]
                project = get_object_or_404(Project, pid=pid)
                c = get_object_or_404(UserProfile, username=request.POST[k])
                project.caretaker_user = c.user
                project.save()
            if k.startswith('item_assigned_'):
                iid = k[len('item_assigned_'):]
                item = get_object_or_404(Item, iid=iid)
                assigned_to = get_object_or_404(
                    UserProfile,
                    username=request.POST[k])
                item.reassign(u, assigned_to, 'deactivating ' + u.username)
                item.save()
            if k.startswith('item_owner_'):
                iid = k[len('item_owner_'):]
                item = get_object_or_404(Item, iid=iid)
                owner = get_object_or_404(
                    UserProfile,
                    username=request.POST[k])
                item.change_owner(u, owner, 'deactivating ' + u.username)
                item.save()
        u.remove_from_all_groups()
        return HttpResponseRedirect(
            reverse('user_detail', args=(u.username,)))


class MilestoneUpdateView(LoggedInMixin, UpdateView):
    model = Milestone
    form_class = MilestoneUpdateForm


class ItemCreateView(LoggedInMixin, CreateView):
    model = Item
    form_class = ItemCreateForm

    def get_success_url(self):
        return reverse('item_detail', args=(self.object.pk,))

    def get_context_data(self, **kwargs):
        ctx = super(ItemCreateView, self).get_context_data(**kwargs)
        mid = self.request.GET.get('mid')
        pid = self.request.GET.get('pid')
        fields = ctx['form'].fields

        if mid:
            milestone = get_object_or_404(Milestone, mid=mid)
            project = milestone.project
            ctx['project'] = project
            fields['milestone'].initial = milestone.mid
            fields['target_date'].initial = milestone.target_date
        elif pid:
            project = get_object_or_404(Project, pid=pid)
            ctx['project'] = project
        else:
            messages.error(self.request,
                           'Couldn\'t find project or milestone.')
            return ctx

        project_milestones = project.milestone_set.order_by('-target_date')
        fields['milestone'].queryset = project_milestones

        fields['project'].initial = project.pid
        fields['project'].queryset = Project.objects.filter(pid=project.pid)

        personnel = project.all_personnel_in_project()
        personnel_qs = User.objects.filter(
            id__in=[up.user.pk for up in personnel]
        ).order_by('last_name').order_by('first_name')

        fields['owner_user'].queryset = personnel_qs
        if self.request.user in personnel_qs:
            fields['owner_user'].initial = self.request.user

        fields['assigned_user'].queryset = personnel_qs

        return ctx


class BugCreateView(LoggedInMixin, CreateView):
    model = Item
    template_name = 'main/bug_form.html'
    form_class = BugCreateForm

    def get_success_url(self):
        return reverse('item_detail', args=(self.object.pk,))

    def get_context_data(self, **kwargs):
        ctx = super(BugCreateView, self).get_context_data(**kwargs)
        mid = self.request.GET.get('mid')
        pid = self.request.GET.get('pid')
        fields = ctx['form'].fields

        if mid:
            milestone = get_object_or_404(Milestone, mid=mid)
            project = milestone.project
            ctx['project'] = project
            fields['milestone'].initial = milestone.mid
            fields['target_date'].initial = milestone.target_date
        elif pid:
            project = get_object_or_404(Project, pid=pid)
            ctx['project'] = project
        else:
            messages.error(self.request,
                           'Couldn\'t find project or milestone.')
            return ctx

        project_milestones = project.milestone_set.order_by('-target_date')
        fields['milestone'].queryset = project_milestones

        fields['project'].initial = project.pid
        fields['project'].queryset = Project.objects.filter(pid=project.pid)

        personnel = project.all_personnel_in_project()
        personnel_qs = User.objects.filter(
            id__in=[up.user.pk for up in personnel]
        ).order_by('last_name').order_by('first_name')

        fields['assigned_user'].queryset = personnel_qs

        fields['owner_user'].initial = self.request.user

        return ctx


class ItemUpdateView(LoggedInMixin, UpdateWithInlinesView):
    model = Item
    form_class = ItemUpdateForm
    inlines = [RemindersInlineFormSet]
    template_name = 'main/item_update_form.html'

    def forms_valid(self, form, inlines):
        for inline in inlines:
            # Connect the current user to the Reminder form
            inline.forms[0].instance.user = self.request.user

        return super(ItemUpdateView, self).forms_valid(form, inlines)


class ItemDeleteView(LoggedInMixin, DeleteView):
    model = Item

    def get_success_url(self):
        return self.object.milestone.get_absolute_url()


class MilestoneDeleteView(LoggedInMixin, DeleteView):
    model = Milestone

    def get_success_url(self):
        return self.object.project.get_absolute_url()


class ItemMoveProjectView(LoggedInMixin, View):
    template_name = "main/item_move_project_form.html"

    def get(self, request, pk):
        item = get_object_or_404(Item, iid=pk)
        return render(request, self.template_name, dict(item=item))

    def post(self, request, pk):
        item = get_object_or_404(Item, iid=pk)
        old_milestone = item.milestone
        project = get_object_or_404(Project, pid=request.POST.get('project'))
        milestone = project.upcoming_milestone()
        item.milestone = milestone
        item.add_project_notification()
        item.save()
        # possibly re-open a milestone
        milestone.update_milestone()
        # possibly close out the old one
        old_milestone.update_milestone()
        return HttpResponseRedirect(item.get_absolute_url())


class ItemSetMilestoneView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, iid=pk)
        old_milestone = item.milestone
        new_milestone = get_object_or_404(
            Milestone, pk=request.POST.get('mid', ''))
        item.milestone = new_milestone
        item.save()
        # possibly re-open a milestone
        new_milestone.update_milestone()
        # possibly close out the old one
        old_milestone.update_milestone()
        return HttpResponse("ok")


class TagListView(LoggedInMixin, ListView):
    model = Tag
    queryset = Tag.objects.all().order_by("name")


class ProjectTagListView(LoggedInMixin, DetailView):
    model = Project
    template_name = "main/project_tags.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectTagListView, self).get_context_data(**kwargs)
        # django-taggit makes this kind of a hard
        # query to express (especially with our lake of
        # regular 'id' columns on legacy tables.)
        # dropping down to raw SQL for this.

        tags = Tag.objects.raw(
            """SELECT t.id as id, t.name as name, t.slug as slug
FROM taggit_tag t, taggit_taggeditem ti, django_content_type dct,
     milestones m, items i
WHERE
  t.id = ti.tag_id
  AND ti.content_type_id = dct.id
  AND m.pid = %s
  AND i.mid = m.mid
  AND ti.object_id = i.iid
  AND dct.model = 'item'""", [self.object.pid])
        tags = list(set(tags))
        tags.sort(key=lambda x: x.name.lower())
        context['tags'] = tags
        return context


class ProjectTagView(LoggedInMixin, View):
    model = Project
    template_name = "main/project_tag.html"

    def get(self, request, pk, slug):
        project = get_object_or_404(Project, pk=pk)
        tag = get_object_or_404(Tag, slug=slug)
        items = Item.objects.raw(
            """SELECT i.iid as iid
FROM taggit_tag t, taggit_taggeditem ti, django_content_type dct,
     milestones m, items i
WHERE
  t.id = ti.tag_id
  AND t.slug = %s
  AND ti.content_type_id = dct.id
  AND m.pid = %s
  AND i.mid = m.mid
  AND ti.object_id = i.iid
  AND dct.model = 'item'""", [slug, project.pid])

        return render(
            request, self.template_name,
            dict(project=project, tag=tag, items=items))


class TagDetailView(LoggedInMixin, DetailView):
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagDetailView, self).get_context_data(**kwargs)

        # this is really terrible, but currently django-taggit has a
        # bug where the TagManager generates incorrect SQL when the
        # content object doesn't use 'id' as its primary key. Ie,
        # the code should look like:
        #
        #        context['items'] = Item.objects.filter(
        #            tags__name__in=[self.object.name])
        #
        # but that generates SQL errors. instead, we use some
        # magic methods and ugly introspection. Once this bug
        # is fixed in taggit, or the PMT is completely migrated
        # and our tables get normal 'id' columns, this can
        # be cleaned up.

        context['items'] = [
            ti.content_object
            for ti
            in self.object.taggit_taggeditem_items.all()
            if ti.content_object.__class__ == Item]

        context['nodes'] = [
            ti.content_object
            for ti
            in self.object.taggit_taggeditem_items.all()
            if ti.content_object.__class__ == Node]
        return context


class NodeReplyView(LoggedInMixin, View):
    def post(self, request, pk):
        node = get_object_or_404(Node, pk=pk)
        user = request.user.userprofile
        body = request.POST.get('body', u'')
        if body == '':
            return HttpResponseRedirect(node.get_absolute_url())

        node.add_reply(user, body)
        node.touch()
        # TODO: preview mode
        # TODO: tags
        statsd.incr('main.forum_reply')
        return HttpResponseRedirect(node.get_absolute_url())


class ProjectRemoveUserView(LoggedInMixin, View):
    template_name = "main/remove_user_confirm.html"

    def get(self, request, pk, username):
        project = get_object_or_404(Project, pid=pk)
        user = get_object_or_404(UserProfile, username=username)
        return render(request, self.template_name,
                      dict(project=project, user=user))

    def post(self, request, pk, username):
        project = get_object_or_404(Project, pid=pk)
        user = get_object_or_404(UserProfile, username=username)
        project.remove_personnel(user)
        return HttpResponseRedirect(
            urljoin(project.get_absolute_url(), '#personnel'))


class ProjectAddPersonnelView(LoggedInMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pid=pk)

        for username in request.POST.getlist('personnel'):
            user = get_object_or_404(
                UserProfile, username=username)
            project.add_personnel(user)

        return HttpResponseRedirect(
            urljoin(project.get_absolute_url(), '#personnel'))


class ProjectAddTodoView(LoggedInMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pid=pk)
        user = request.user.userprofile
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
        user = request.user.userprofile
        project = get_object_or_404(Project, pid=pk)
        title = request.POST.get('title', u"Untitled")
        if len(title) == 0:
            title = "Untitled"
        tags = clean_tags(request.POST.get('tags', u''))
        description = request.POST.get('description', u'')

        assigned_to = request.POST.getlist('assigned_to')
        assignees = []
        for username in assigned_to:
            assignee = get_object_or_404(UserProfile, username=username)
            assignees.append(assignee)

        owner = get_object_or_404(
            UserProfile, username=request.POST.get(
                'owner', user.username))
        milestone = get_object_or_404(
            Milestone, mid=request.POST.get('milestone'))
        priority = request.POST.get('priority', '1')
        target_date = request.POST.get('target_date') or milestone.target_date

        remind_me_toggle = request.POST.get('remind_me_toggle')
        reminder_duration = None
        if remind_me_toggle == 'on':
            reminder_time = request.POST.get('reminder_time')
            reminder_unit = request.POST.get('reminder_unit', u'd')
            reminder_duration = reminder_time + reminder_unit

        for assignee in assignees:
            project.add_item(
                type=self.item_type,
                title=title,
                assigned_to=assignee,
                owner=owner,
                milestone=milestone,
                priority=priority,
                description=description,
                estimated_time=request.POST.get('estimated_time', '1 hour'),
                status='OPEN',
                r_status='',
                tags=tags,
                target_date=target_date,
                reminder_duration=reminder_duration,
                current_user=request.user
            )
        statsd.incr('main.%s_added' % (self.item_type.replace(' ', '_')))
        return HttpResponseRedirect(project.get_absolute_url())


class ProjectAddNodeView(LoggedInMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pid=pk)
        user = request.user.userprofile
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
        body = request.POST.get('body', u'')
        if body == '':
            return HttpResponseRedirect(project.get_absolute_url())
        StatusUpdate.objects.create(
            project=project, body=body, author=request.user)
        statsd.incr('main.status_update')
        return HttpResponseRedirect(project.get_absolute_url())


class ProjectAddMilestoneView(LoggedInMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pid=pk)
        name = request.POST.get('name', u'Untitled milestone')
        if len(name) == 0:
            name = "Untitled milestone"
        try:
            Milestone.objects.create(
                project=project, name=name,
                status='OPEN',
                description=request.POST.get('description', ''),
                target_date=request.POST.get('target_date',
                                             timezone.now().date())
            )
        except ValidationError, e:
            for mesg in e.messages:
                messages.error(
                    self.request,
                    mark_safe(  # nosec
                        'The "{}" milestone wasn\'t created. {}'.format(
                            name, mesg)))
        return HttpResponseRedirect(project.get_absolute_url() + '#milestones')


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
        now = timezone.now()
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
            'item', 'user', 'item__milestone',
            'item__milestone__project')
        all_active_items = set([a.item for a in times_logged])
        all_active_projects = set(
            [i.milestone.project for i in all_active_items])
        all_active_users = set([a.user.userprofile for a in times_logged])

        for p in all_active_projects:
            p.recent_hours = interval_sum(
                [a.actual_time for a in times_logged
                 if a.item.milestone.project == p]).total_seconds() / 3600.

        for u in all_active_users:
            u.recent_hours = interval_sum(
                [a.actual_time for a in times_logged
                 if a.user.userprofile == u]).total_seconds() / 3600.

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


class SignS3View(LoggedInMixin, BaseSignS3View):
    def get_bucket(self):
        return settings.AWS_S3_UPLOAD_BUCKET

    def extension(self, request):
        object_name = safe_basename(
            request.GET.get('s3_object_name', 'unknown.obj'))
        mime_type = request.GET.get('s3_object_type')
        (_, extension) = ntpath.splitext(object_name)
        # force the extension for some known cases
        if 'jpeg' in mime_type:
            extension = ".jpg"
        elif 'png' in mime_type:
            extension = ".png"
        elif 'gif' in mime_type:
            extension = ".gif"
        return extension

    def basename(self, request):
        object_name = safe_basename(
            request.GET.get(self.get_name_field(), 'unknown.obj'))
        (basename, _) = ntpath.splitext(object_name)
        uid = str(uuid.uuid4())
        return basename + "-" + uid


class ItemAddAttachmentView(LoggedInMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        title = request.POST.get('title', 'no title')
        description = request.POST.get('description', '')
        url = request.POST.get('s3_url')
        filename = url.split('/')[-1]
        atype = 'obj'
        if url.endswith('png'):
            atype = 'png'
        if url.endswith('jpg'):
            atype = 'jpg'
        if url.endswith('gif'):
            atype = 'gif'
        Attachment.objects.create(
            item=item,
            user=request.user,
            url=url,
            title=title,
            description=description,
            filename=filename,
            type=atype,
            last_mod=timezone.now(),
        )
        return HttpResponseRedirect(item.get_absolute_url())


class DeleteAttachmentView(LoggedInMixin, DeleteView):
    model = Attachment

    def get_success_url(self):
        return self.object.item.get_absolute_url()


class GroupDetailView(LoggedInMixin, DetailView):
    template_name = "main/group_detail.html"
    model = UserProfile

    def get_context_data(self, **kwargs):
        ctx = super(GroupDetailView, self).get_context_data(**kwargs)
        group = ctx.get('object')

        primary_members = UserProfile.objects.filter(
            primary_group=ctx.get('object')
        ).exclude(status='inactive').order_by('fullname')

        other_members = UserProfile.objects.filter(
            ingroup__grp=group
        ).exclude(status='inactive').order_by('fullname')

        eligible_users = UserProfile.objects.filter(
            status='active'
        ).filter(
            ~Q(pk__in=other_members),
            ~Q(pk=group.pk),
        ).exclude(status='inactive')

        ctx.update({
            'primary_members': primary_members,
            'other_members': other_members,
            'eligible_users': eligible_users,
        })
        return ctx


class RemoveUserFromGroupView(LoggedInMixin, View):
    def post(self, request, pk):
        InGroup.objects.filter(
            grp__username=pk,
            username__username=request.POST.get('username')).delete()
        return HttpResponseRedirect(reverse('group_detail', args=(pk,)))


class AddUserToGroupView(LoggedInMixin, View):
    def post(self, request, pk):
        g = get_object_or_404(UserProfile, username=pk)
        u = get_object_or_404(
            UserProfile, username=request.POST.get('username'))
        ig, _created = InGroup.objects.get_or_create(grp=g, username=u)
        return HttpResponseRedirect(reverse('group_detail', args=(pk,)))


class GroupListView(LoggedInMixin, ListView):
    template_name = "main/group_list.html"
    model = UserProfile

    def get_queryset(self):
        groups = UserProfile.objects.filter(grp=True)

        group_list = [(group.username, InGroup.verbose_name(group.fullname))
                      for group in groups]

        return group_list


class AddTrackersView(LoggedInMixin, FormSetView):
    template_name = "main/add_trackers.html"
    form_class = AddTrackerForm
    extra = 10
    success_message = 'Tracker added for project: ' + \
                      '<strong>' + \
                      '<a href="%(project_link)s">%(project_name)s</a>' + \
                      '</strong>'
    error_message = 'Error adding tracker: ' + \
                    '<strong>%(error_text)s</strong>'

    def formset_valid(self, formset):
        for form in formset.forms:
            if form.cleaned_data == {}:
                continue

            self.handle_formset_row(form, self.request.user)

        return super(AddTrackersView, self).formset_valid(formset)

    def handle_formset_row(self, form, user):
        project = form.cleaned_data.get('project')
        task = form.cleaned_data.get('task')
        time = form.cleaned_data.get('time', '1 hour')
        client_uni = form.cleaned_data.get('client_uni')

        project.add_tracker(user, task, time, client_uni)
        messages.success(
            self.request,
            self.success_message % dict(
                project_link=reverse('project_detail',
                                     args=(project.pk,)),
                project_name=project.name)
        )


def server_error(request, template_name='500.html'):
    return render(
        request,
        template_name,
    )

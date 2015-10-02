from django import forms
from django.contrib.auth.models import User
from django.db import connection, models
from django.db.models import Max, Sum
from django.db.models.signals import post_save
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil import parser
from interval.fields import IntervalField
from taggit.managers import TaggableManager
from django.core.mail import send_mail
from django_statsd.clients import statsd
from simpleduration import Duration, InvalidDuration
from .timeline import (
    TimeLineEvent, TimeLineComment,
    TimeLinePost, TimeLineActualTime, TimeLineStatus,
    TimeLineMilestone)
import re
import textwrap


class UserProfile(models.Model):
    username = models.CharField(max_length=32, primary_key=True)
    fullname = models.CharField(max_length=128, blank=True)
    email = models.CharField(max_length=32)
    status = models.CharField(max_length=16, blank=True)
    grp = models.BooleanField(default=False)
    type = models.TextField(blank=True)
    title = models.TextField(blank=True)
    phone = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    photo_url = models.TextField(blank=True)
    photo_width = models.IntegerField(null=True, blank=True)
    photo_height = models.IntegerField(null=True, blank=True)
    campus = models.TextField(blank=True)
    building = models.TextField(blank=True)
    room = models.TextField(blank=True)
    user = models.OneToOneField(User)
    primary_group = models.ForeignKey('UserProfile',
                                      blank=True,
                                      null=True,
                                      limit_choices_to={'grp': True})

    class Meta:
        db_table = u'users'
        ordering = ['fullname']

    def __unicode__(self):
        return self.fullname

    def get_absolute_url(self):
        if self.grp:
            return reverse("group_detail", args=(self.username,))
        else:
            return reverse("user_detail", args=(self.username,))

    def active(self):
        return self.status == 'active'

    def active_projects(self, start, end):
        return set(a.item.milestone.project
                   for a in self.resolve_times_for_interval(start, end))

    def has_recent_active_projects(self):
        now = timezone.now()
        start = now - timedelta(weeks=5)
        return self.actualtime_set.filter(
            completed__gte=start, completed__lte=now).count() > 0

    def recent_active_projects(self):
        """ any projects touched in the last year """
        now = timezone.now()
        start = now - timedelta(weeks=5)
        projects = Project.objects.raw(
            'SELECT distinct m.pid as pid '
            'FROM milestones m, items i, actual_times a '
            'WHERE m.mid = i.mid AND i.iid = a.iid '
            'AND a.user_id = %s '
            'AND a.completed > %s '
            'AND a.completed < %s', [self.user.id, start, now])
        return sorted(set(list(projects)), key=lambda x: x.name.lower())

    def resolve_times_for_interval(self, start, end):
        return ActualTime.objects.filter(
            user=self.user,
            completed__gt=start,
            completed__lte=end
        ).select_related('item', 'item__milestone', 'item__milestone__project')

    def total_resolve_times(self):
        return interval_sum(
            a.actual_time for a in ActualTime.objects.filter(
                user=self.user)).total_seconds() / 3600.

    def total_assigned_time(self):
        return interval_sum(
            [
                i.estimated_time
                for i in Item.objects.filter(
                    assigned_to=self,
                    status='OPEN')]).total_seconds() / 3600.

    def interval_time(self, start, end):
        return interval_sum(
            [a.actual_time
             for a in self.resolve_times_for_interval(start, end)])

    def weekly_report(self, week_start, week_end):
        # TODO: rename to something more generic now that this is
        # used for more than just weekly reports
        active_projects = self.active_projects(week_start, week_end)
        # google pie chart needs max
        max_time = timedelta()
        total_time = timedelta()
        for project in active_projects:
            pu = ProjectUser(project, self)
            ptime = pu.completed_time_for_interval(week_start, week_end)
            max_time = max(ptime, max_time)
            total_time += ptime
            project.time = ptime
        return dict(
            active_projects=active_projects,
            max_time=max_time,
            total_time=total_time,
            individual_times=self.resolve_times_for_interval(
                week_start, week_end),
        )

    def open_assigned_items(self):
        return Item.objects.filter(
            assigned_to=self,
            status__in=['OPEN', 'UNASSIGNED', 'INPROGRESS']
            ).exclude(
            milestone__name='Someday/Maybe').select_related(
                'milestone', 'milestone__project', 'owner', 'assigned_to')

    def open_owned_items(self):
        """ for the 'owned items' page. """
        return Item.objects.filter(
            owner=self,
            status__in=['OPEN', 'UNASSIGNED', 'INPROGRESS', 'RESOLVED']
        ).exclude(
            assigned_to=self
        ).order_by('-priority', '-target_date').select_related(
            'milestone', 'milestone__project', 'assigned_to')

    def resolved_owned_items(self):
        return Item.objects.filter(
            owner=self,
            status='RESOLVED'
            ).select_related(
                'milestone', 'milestone__project', 'owner', 'assigned_to')

    def non_verified_owned_items(self):
        """ all items that this user owns that
        are OPEN, INPROGRESS, or RESOLVED"""
        return Item.objects.filter(
            owner=self,
            ).exclude(status='VERIFIED').select_related(
            'milestone', 'milestone__project')

    def non_verified_assigned_items(self):
        """ all items assigned to this user that
        are OPEN, INPROGRESS, or RESOLVED"""
        return Item.objects.filter(
            assigned_to=self,
            ).exclude(status='VERIFIED').select_related(
            'milestone', 'milestone__project')

    def items(self):
        assigned = set(self.open_assigned_items())
        owned = set(self.resolved_owned_items())
        items = list(assigned.union(owned))
        items = sorted(items, key=lambda x: (-x.priority, x.target_date))
        return items

    def clients(self):
        return Client.objects.filter(user__userprofile=self)

    def manager_on(self):
        return [w.project for w in self.workson_set.filter(
                auth='manager').select_related('project')]

    def developer_on(self):
        return [w.project for w in self.workson_set.filter(
                auth='developer').select_related('project')]

    def guest_on(self):
        return [w.project for w in self.workson_set.filter(
                auth='guest').select_related('project')]

    def personnel_on(self):
        return [w.project for w
                in self.workson_set.all(
                ).select_related('project').order_by('project__name')]

    def total_group_time(self, start, end):
        return interval_sum(
            [u.interval_time(start, end) for u in self.users_in_group()])

    def user_groups(self):
        return [ig.grp for ig in self.ingroup_set.all()]

    def users_in_group(self):
        return [ig.username for ig in self.group_members.all()]

    def recent_forum_posts(self, count=10):
        return Node.objects.filter(user=self.user)[:count]

    def recent_status_updates(self, count=20):
        return self.statusupdate_set.all()[:count]

    def progress_report(self):
        now = timezone.now()
        monday = now + timedelta(days=-now.weekday())
        week_start = datetime.combine(monday, datetime.min.time())
        hours_logged = self.interval_time(
            week_start,
            week_start + timedelta(days=7))
        hours_logged = hours_logged.total_seconds() / 3600.
        week_percentage = min(
            int((hours_logged / 35.) * 100),
            100)
        target_hours = min(now.weekday(), 5) * 7
        target_percentage = min(int((target_hours / 35.) * 100), 100)
        return dict(hours_logged=hours_logged,
                    week_percentage=week_percentage,
                    target_hours=target_hours,
                    target_percentage=target_percentage,
                    behind=week_percentage < (target_percentage - 20))

    def send_weekly_report(self):
        r = self.progress_report()
        body = self.weekly_report_email_body(r['hours_logged'], r['behind'])
        send_mail(
            "PMT Weekly Report",
            body, settings.SERVER_EMAIL,
            [self.email], fail_silently=settings.DEBUG)

    def weekly_report_email_body(self, hours_logged, behind):
        if behind:
            return (
                """This week you have only logged %.1f hours.\n\n"""
                """Now is a good time to take care of that.\n"""
                % hours_logged)
        else:
            return (
                """You've logged %.1f hours this week. Good job!\n"""
                % hours_logged)

    def group_fullname(self):
        f = self.fullname
        return f.replace(" (group)", "")

    def remove_from_all_groups(self):
        self.ingroup_set.all().delete()

    def timeline(self, start=None, end=None):
        all_events = []
        if end is None:
            end = timezone.now()

        if start is None:
            start = end - timedelta(weeks=1)

        events = Comment.objects.filter(
            username=self.username,
            add_date_time__gte=start.date(),
            add_date_time__lte=end,
        ).exclude(event=None).select_related(
            'event__item', 'event__item__milestone',
            'event__item__milestone__project',
            'event', 'item')
        all_events.extend([TimeLineEvent(c) for c in events])

        comments = Comment.objects.filter(
            username=self.username,
            event=None,
            add_date_time__gte=start.date(),
            add_date_time__lte=end,
        ).select_related('item', 'item__milestone', 'item__milestone__project')
        all_events.extend([TimeLineComment(c) for c in comments])

        actual_times = ActualTime.objects.filter(
            user=self.user,
            completed__gte=start.date(),
            completed__lte=end,
        ).select_related('item', 'item__milestone', 'item__milestone__project')
        all_events.extend([TimeLineActualTime(a) for a in actual_times])

        statuses = StatusUpdate.objects.filter(
            user=self,
            added__gte=start.date(),
            added__lte=end,
        ).select_related('project')
        all_events.extend([TimeLineStatus(s) for s in statuses])

        posts = Node.objects.filter(
            user=self.user,
            added__gte=start.date(),
            added__lte=end,
        ).select_related('project')
        all_events.extend([TimeLinePost(p) for p in posts])

        all_events.sort()
        all_events.reverse()
        return all_events

    def passed_open_milestones(self):
        return Milestone.objects.filter(
            project__caretaker_user=self.user,
            status='OPEN',
            target_date__lt=timezone.now(),
        ).order_by('target_date').select_related('project')


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            username=instance.username,
            fullname=instance.get_full_name(),
            email=instance.email,
            status='active',
        )

post_save.connect(create_user_profile, sender=User)


class ProjectUser(object):
    def __init__(self, project, user):
        self.project = project
        self.user = user

    def completed_time_for_interval(self, start, end):
        return interval_sum(
            [
                a.actual_time for a in ActualTime.objects.filter(
                    user=self.user.user,
                    item__milestone__project=self.project,
                    completed__gt=start,
                    completed__lte=end)])


# before putting in the IntervalField, there were some
# weird mismatches between what postgres would return
# and what factory_boy models would return for intervals
# this function hid the difference. Now, it looks like
# it might be unecessary. can probably remove this
# and replace with a plain sum() once a little
# more testing is done
def interval_sum(intervals):
    total = timedelta()
    for a in filter(None, intervals):
        total += a
    return total


# Avoid BadHeaderError - The subject can't contain newlines.
def clean_subject(s):
    return s.replace('\n', ' ').replace('\r', '')

PROJECT_STATUS_CHOICES = [
    "New", "Development", "Deployment", "Defunct",
    "Deferred", "Non-project",
]


class Project(models.Model):
    pid = models.AutoField(primary_key=True)
    name = models.CharField("Project name", max_length=255)
    projnum = models.IntegerField("Project number", null=True, blank=True)
    pub_view = models.BooleanField("PMT View", default=False)
    caretaker_user = models.ForeignKey(User, null=True)
    description = models.TextField(blank=True)
    url = models.CharField("Project URL", max_length=255, blank=True)
    info_url = models.CharField("Information URL", max_length=255, blank=True)
    eval_url = models.CharField("Evaluation URL", max_length=255, blank=True)
    wiki_category = models.CharField(max_length=256, blank=True)
    status = models.CharField(
        max_length=16, blank=True,
        default="New",
        choices=[(c, c) for c in PROJECT_STATUS_CHOICES])
    entry_rel = models.BooleanField("Released", default=False)
    poster = models.BooleanField("Poster project", default=False)
    type = models.CharField(max_length=50, blank=True)
    area = models.CharField("Discipline", max_length=100, blank=True)
    restricted = models.CharField(max_length=10, blank=True)
    approach = models.CharField(max_length=50, blank=True)
    scale = models.CharField(max_length=20, blank=True)
    distrib = models.CharField("Distribution", max_length=20, blank=True)

    class Meta:
        db_table = u'projects'
        ordering = ['name', ]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/project/%d/" % self.pid

    def active_items(self):
        return Item.objects.filter(
            milestone__project=self,
            status__in=['OPEN', 'RESOLVED', 'INPROGRESS'])

    def milestones(self):
        return Milestone.objects.filter(project=self).order_by('target_date')

    def open_milestones(self):
        return self.milestone_set.filter(status='OPEN').order_by('target_date')

    def managers(self):
        return [w.username for w in self.workson_set.filter(auth='manager')]

    def developers(self):
        return [w.username for w in self.workson_set.filter(auth='developer')]

    def guests(self):
        return [w.username for w in self.workson_set.filter(auth='guest')]

    def add_manager(self, user):
        self.add_personnel(user, auth='manager')

    def add_developer(self, user):
        self.add_personnel(user, auth='developer')

    def add_guest(self, user):
        self.add_personnel(user, auth='guest')

    def add_milestone(self, name, target_date, description):
        if not re.match(r'\d{4}-\d{1,2}-\d{1,2}', target_date):
            raise forms.ValidationError(
                'Invalid target date: %s' % target_date)

        milestone = Milestone.objects.create(
            name=name,
            target_date=target_date,
            project=self,
            description=description)

        return milestone.mid

    def add_personnel(self, user, auth='guest'):
        # make sure we don't duplicate any
        WorksOn.objects.filter(project=self, user=user.user).delete()
        WorksOn.objects.create(username=user, project=self, auth=auth,
                               user=user.user)

    def set_personnel(self, users, auth='guest'):
        WorksOn.objects.filter(project=self, auth=auth).delete()
        for u in users:
            self.add_personnel(u, auth)

    def set_managers(self, users):
        self.set_personnel(users, auth='manager')

    def set_developers(self, users):
        self.set_personnel(users, auth='developer')

    def set_guests(self, users):
        self.set_personnel(users, auth='guest')

    def remove_personnel(self, user):
        WorksOn.objects.filter(project=self, user=user.user).delete()

    def all_users_not_in_project(self):
        already_in = set(
            [w.username
             for w in WorksOn.objects.filter(
                 project=self).select_related('user')])
        all_users = set(UserProfile.objects.filter(status='active'))
        return sorted(list(all_users - already_in),
                      key=lambda x: x.fullname.lower())

    def upcoming_milestone(self):
        # ideally, we want a milestone that is open, in the future,
        # and as close to today as possible

        if not self.milestone_set.exists():
            # there are no milestones, nothing we can do
            return None

        r = self.milestone_set.filter(
            status='OPEN',
            target_date__gte=timezone.now())
        if r.count():
            return r.order_by('target_date')[0]
        # there aren't any upcoming open milestones, but we need
        # to return *something*, so we'll just go with the latest
        # milestone.
        return self.milestone_set.all().order_by("-target_date")[0]

    def add_todo(self, user, title, tags=None):
        milestone = self.upcoming_milestone()
        item = Item.objects.create(
            milestone=milestone,
            type='action item',
            owner=user,
            owner_user=user.user,
            assigned_to=user,
            assigned_user=user.user,
            title=title,
            priority=1,
            status='OPEN',
            r_status='',
            estimated_time='0',
            target_date=milestone.target_date,
            last_mod=timezone.now(),
            description='')
        item.add_event('OPEN', user, "<b>Action item added</b>")
        if tags:
            item.tags.add(*tags)
        milestone.update_milestone()

    def add_item(self, type='action item', title="",
                 assigned_to=None, owner=None, milestone=None,
                 priority=1, description="", estimated_time="1 hour",
                 status='OPEN', r_status='',
                 tags=None, target_date=None, email_everyone=False):
        try:
            d = Duration(estimated_time)
        except InvalidDuration:
            d = Duration("0 minutes")
        td = d.timedelta()

        try:
            # Attempt to parse the date.
            target_date = parser.parse(target_date).date()
        except AttributeError:
            # If we can't parse it, it must be a datetime object, so let it
            # through.
            pass

        item = Item.objects.create(
            milestone=milestone,
            type=type,
            owner=owner,
            owner_user=owner.user,
            assigned_to=assigned_to,
            assigned_user=assigned_to.user,
            title=title,
            priority=priority,
            status=status,
            r_status=r_status,
            estimated_time=td,
            target_date=target_date,
            last_mod=timezone.now(),
            description=description)
        item.add_event('OPEN', owner, "<b>%s added</b>" % type.capitalize())
        if tags:
            item.tags.add(*tags)
        item.setup_default_notification()
        item.add_project_notification()
        item.update_email(
            "%s added\n----\n%s"
            % (type.capitalize(), description),
            owner,
            skip_self=(not email_everyone),
        )
        milestone.update_milestone()
        return item

    def recent_forum_posts(self, count=10):
        return self.node_set.all()[:count]

    def recent_status_updates(self, count=20):
        return self.statusupdate_set.all()[:count]

    def add_node(self, subject, user, body, tags=None):
        n = Node.objects.create(
            subject=subject,
            body=body,
            user=user.user,
            reply_to=0,
            replies=0,
            type='post',
            added=timezone.now(),
            modified=timezone.now(),
            project=self)
        if tags:
            n.tags.add(*tags)
        self.email_post(n, body, user)

    def email_post(self, node, body, user):
        body = textwrap.fill(body, replace_whitespace=False)
        body = """
Project: %s
Author: %s
Forum title: %s

%s


-- \nThis message sent automatically by the PMT forum.
To reply, please visit <https://pmt.ccnmtl.columbia.edu%s>\n
        """ % (
            self.name,
            user.fullname,
            node.subject,
            body,
            node.get_absolute_url())
        addresses = [
            u.email for u in self.all_personnel_in_project()
            if u != user]
        subject = "[PMT Forum: %s] %s" % (self.name, node.subject)

        statsd.incr('main.email_sent')
        send_mail(clean_subject(subject), body, user.email,
                  addresses, fail_silently=settings.DEBUG)

    def personnel_in_project(self):
        """ return list of all users/groups in project

        sorted with groups first, then individual users,
        sorted alphabetically by fullname """
        return sorted(
            [
                w.user.userprofile for w in WorksOn.objects.filter(
                    project=self
                ).select_related('user')
                if w.user.userprofile.status == 'active'],
            key=lambda user: (not user.grp, user.fullname.lower()))

    def all_personnel_in_project(self):
        users = set([u for u in self.personnel_in_project()
                     if not u.grp])
        groups = [u for u in self.personnel_in_project()
                  if u.grp]
        for g in groups:
            users.update(g.users_in_group())
        return sorted(list(users), key=lambda user: user.fullname.lower())

    def current_date(self):
        """ very simple helper that makes it easier to set the
        default date on add-* forms"""
        return timezone.now().date()

    def group_hours(self, group, start, end):
        cursor = connection.cursor()
        cursor.execute("""
SELECT SUM(a.actual_time) AS hours
FROM actual_times a, in_group g, milestones m, items i, users u
WHERE a.iid = i.iid
    AND i.mid = m.mid
    AND m.pid = %s
    AND a.user_id = u.user_id
    AND g.username = u.username
    AND g.grp  = %s
    AND a.completed > %s
    AND a.completed <= %s
        """, [self.pid, group, start, end])
        row = cursor.fetchone()
        time = row[0]
        return time if time else timedelta(0)

    def interval_total(self, start, end):
        cursor = connection.cursor()
        cursor.execute("""
SELECT SUM(a.actual_time) AS total_time
FROM actual_times a, items i, milestones m, in_group g, users u
WHERE a.iid = i.iid
    AND i.mid = m.mid
    AND m.pid = %s
    AND a.user_id = u.user_id
    AND g.username = u.username
    AND g.grp IN ('grp_programmers','grp_webmasters','grp_video',
        'grp_educationaltechnologists','grp_management')
    AND a.completed > %s
    AND a.completed <= %s
        """, [self.pid, start, end])
        row = cursor.fetchone()
        time = row[0]
        return time if time else timedelta(0)

    @staticmethod
    def projects_active_during(start, end, groups):
        groups_string = ','.join([x.username for x in groups])
        projects = Project.objects.raw("""
SELECT DISTINCT p.pid, p.name, p.projnum
FROM projects p, milestones m, items i, actual_times a, in_group g, users u
WHERE p.pid = m.pid
    AND m.mid = i.mid
    AND i.iid = a.iid
    AND a.user_id = u.user_id
    AND g.username = u.username
    AND g.grp = ANY (string_to_array(%s, ',')::text[])
    AND a.completed > %s
    AND a.completed <= %s
ORDER BY p.projnum
        """, [groups_string, start, end])
        return projects

    @staticmethod
    def projects_active_between(start, end):
        """ Return projects active between the given dates. """
        projects = Project.objects.filter(
            milestone__item__actualtime__completed__gte=start,
            milestone__item__actualtime__completed__lte=end,
        ).annotate(
            last_worked_on=Max('milestone__item__actualtime__completed'),
            hours_logged=Sum('milestone__item__actualtime__actual_time'),
        ).order_by('-hours_logged')
        return projects

    def last_mod(self):
        r = Item.objects.filter(
            milestone__project=self).order_by("-last_mod")
        try:
            return r[0].last_mod
        except IndexError:
            return None

    def all_actual_times(self):
        return ActualTime.objects.filter(
            item__milestone__project=self,
        ).order_by('completed')

    def users_active_between(self, start, end):
        """Returns a project report that lists user stats."""
        active_users = User.objects.filter(
            actualtime__item__milestone__project=self,
            actualtime__completed__gt=start,
            actualtime__completed__lt=end
        ).distinct().annotate(
            last_worked_on=Max('actualtime__completed'),
            hours_logged=Sum('actualtime__actual_time'),
        ).order_by('-hours_logged')

        return active_users

    def timeline(self, start=None, end=None):
        all_events = []
        if end is None:
            end = timezone.now()

        if start is None:
            start = end - timedelta(weeks=1)

        events = Comment.objects.filter(
            event__item__milestone__project=self,
            add_date_time__gte=start.date(),
            add_date_time__lte=end,
        ).select_related('event__item', 'event__item__milestone',
                         'event__item__milestone__project',
                         'event', 'item')
        all_events.extend([TimeLineEvent(c) for c in events])

        comments = Comment.objects.filter(
            item__milestone__project=self,
            add_date_time__gte=start.date(),
            add_date_time__lte=end,
        ).select_related('item', 'item__milestone', 'item__milestone__project')
        all_events.extend([TimeLineComment(c) for c in comments])

        actual_times = ActualTime.objects.filter(
            item__milestone__project=self,
            completed__gte=start.date(),
            completed__lte=end,
        ).select_related('item', 'item__milestone', 'item__milestone__project',
                         'user')
        all_events.extend([TimeLineActualTime(a) for a in actual_times])

        statuses = StatusUpdate.objects.filter(
            project=self,
            added__gte=start.date(),
            added__lte=end,
        ).select_related('project', 'user')
        all_events.extend([TimeLineStatus(s) for s in statuses])

        posts = Node.objects.filter(
            project=self,
            added__gte=start.date(),
            added__lte=end,
        ).select_related('project', 'user')
        all_events.extend([TimeLinePost(p) for p in posts])

        milestones = Milestone.objects.filter(
            project=self,
            target_date__gte=start.date(),
            target_date__lte=end,
        )
        all_events.extend(TimeLineMilestone(m) for m in milestones)

        all_events.sort()
        all_events.reverse()
        return all_events


class Document(models.Model):
    did = models.AutoField(primary_key=True)
    pid = models.ForeignKey(Project, db_column='pid')
    filename = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=8, blank=True)
    url = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=16, blank=True)
    user = models.ForeignKey(User)
    last_mod = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'documents'


class Milestone(models.Model):
    mid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    target_date = models.DateField()
    project = models.ForeignKey(Project, db_column='pid')
    status = models.CharField(max_length=8, default='OPEN')
    description = models.TextField(blank=True)

    class Meta:
        db_table = u'milestones'
        ordering = ['target_date', 'name', ]

    def active_items(self):
        return Item.objects.filter(
            milestone=self,
            status__in=['OPEN', 'RESOLVED', 'INPROGRESS']
        ).order_by('-target_date').select_related(
            'owner_user', 'assigned_user',
            'owner_user__userprofile', 'assigned_user__userprofile')

    def get_absolute_url(self):
        return "/milestone/%d/" % self.mid

    def status_class(self):
        s = self.status.lower()
        if (s == 'open'):
            s = 'dmt-' + s
        return s

    def is_open(self):
        return self.status == 'OPEN'

    def is_empty(self):
        return self.item_set.count() == 0

    def num_open_items(self):
        return self.item_set.filter(status='OPEN').count()

    def estimated_time_remaining(self):
        return interval_sum(
            [i.estimated_time for i in self.item_set.filter(status='OPEN')]
        ).total_seconds() / 3600.

    def total_estimated_hours(self):
        return interval_sum(
            [i.estimated_time for i in self.item_set.all()]
        ).total_seconds() / 3600.

    def hours_completed(self):
        return interval_sum(
            [a.actual_time
             for a in ActualTime.objects.filter(item__milestone=self)]
        ).total_seconds() / 3600.

    def update_milestone(self):
        if self.should_be_closed():
            self.close_milestone()
        else:
            self.open_milestone()

    def should_be_closed(self):
        if self.target_date_passed():
            # target date passed but there are open items
            return self.num_unclosed_items() == 0
        # target date hasn't passed yet
        return False

    def close_milestone(self):
        if self.status != "CLOSED":
            self.status = "CLOSED"
            self.save()
            statsd.incr('main.milestone_closed')

    def open_milestone(self):
        self.status = "OPEN"
        self.save()

    def target_date_passed(self):
        return self.target_date < timezone.now().date()

    def num_unclosed_items(self):
        return self.item_set.filter(
            status__in=['OPEN', 'INPROGRESS', 'RESOLVED']).count()

    def sorted_items(self):
        return self.item_set.order_by('status', '-target_date')

    def __unicode__(self):
        return self.name


def priority_label_f(priority):
    labels = ['ICING', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    return labels[priority]


class Item(models.Model):
    iid = models.AutoField(primary_key=True)
    type = models.CharField(
        max_length=12,
        choices=[('bug', 'bug'), ('action item', 'action item')])
    owner = models.ForeignKey(UserProfile, db_column='owner',
                              related_name='owned_items')
    owner_user = models.ForeignKey(User, null=True, db_column='owner_user',
                                   related_name='owned_items')
    assigned_to = models.ForeignKey(UserProfile, db_column='assigned_to',
                                    related_name='assigned_items')
    assigned_user = models.ForeignKey(User, null=True,
                                      db_column='assigned_user',
                                      related_name='assigned_to')
    title = models.CharField(max_length=255)
    milestone = models.ForeignKey(Milestone, db_column='mid', db_index=True)
    status = models.CharField(
        max_length=16,
        db_index=True,
        choices=[
            ('OPEN', 'OPEN'),
            ('INPROGRESS', 'IN PROGRESS'),
            ('RESOLVED', 'RESOLVED'),
            ('VERIFIED', 'VERIFIED')])
    description = models.TextField(blank=True)
    priority = models.IntegerField(
        null=True, blank=True,
        choices=[
            (0, 'ICING'), (1, 'LOW'), (2, 'MEDIUM'),
            (3, 'HIGH'), (4, 'CRITICAL')])
    r_status = models.CharField(max_length=16, blank=True)
    last_mod = models.DateTimeField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    estimated_time = IntervalField(blank=True, null=True)
    url = models.TextField(blank=True)

    tags = TaggableManager()

    class Meta:
        db_table = u'items'

    def get_absolute_url(self):
        return "/item/%d/" % self.iid

    def status_class(self):
        s = self.status.lower()
        if (s == 'open'):
            s = 'dmt-' + s
        return s

    def priority_label(self):
        return priority_label_f(self.priority)

    def status_display(self):
        if self.status == 'RESOLVED':
            return self.r_status
        return self.status

    def target_date_status(self):
        overdue = 0
        if self.target_date:
            overdue = (timezone.now().date() - self.target_date).days
        return overdue_days_to_string(overdue)

    def is_bug(self):
        return self.type == "bug"

    def history(self):
        """ interleave comments and events into one stream """
        comments = [HistoryComment(c) for c in self.comment_set.all()]
        events = [HistoryEvent(e) for e in self.events_set.all()]
        merged = comments + events
        merged.sort()
        return merged

    def get_resolve_time(self):
        total = ActualTime.objects.filter(item=self).aggregate(
            Sum('actual_time'))
        return total['actual_time__sum']

    def add_resolve_time(self, user, time, completed=None):
        if not completed:
            completed = timezone.now()
        ActualTime.objects.create(
            item=self,
            resolver=user,
            user=user.user,
            actual_time=time,
            completed=completed)

    def add_clients(self, clients):
        for c in clients:
            ItemClient.objects.create(item=self, client=c)

    def resolvable(self):
        return self.status in ['OPEN', 'INPROGRESS', 'NEW']

    def inprogressable(self):
        return self.status == 'OPEN'

    def verifiable(self):
        return self.status == 'RESOLVED'

    def reopenable(self):
        return self.status in ['RESOLVED', 'INPROGRESS', 'VERIFIED', 'CLOSED']

    def touch(self):
        self.last_mod = timezone.now()
        self.save()

    def add_comment(self, user, comment_src, rendered_comment):
        Comment.objects.create(
            item=self,
            username=user.username,
            comment_src=comment_src,
            comment=rendered_comment,
            add_date_time=timezone.now())

    def resolve(self, user, r_status, comment):
        self.status = "RESOLVED"
        self.r_status = r_status
        self.save()
        e = Events.objects.create(
            status="RESOLVED",
            event_date_time=timezone.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment="<b>Resolved %s</b><br />\n%s" % (r_status, comment),
            add_date_time=timezone.now())

    def verify(self, user, comment):
        self.status = 'VERIFIED'
        self.r_status = ''
        self.save()
        e = Events.objects.create(
            status="VERIFIED",
            event_date_time=timezone.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment="<b>Verified</b><br />\n%s" % comment,
            add_date_time=timezone.now())

    def mark_in_progress(self, user, comment):
        self.status = 'INPROGRESS'
        self.r_status = ''
        self.save()
        e = Events.objects.create(
            status="INPROGRESS",
            event_date_time=timezone.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment="<b>Marked as In-progress</b><br />\n%s" % comment,
            add_date_time=timezone.now())

    def reopen(self, user, comment):
        self.status = 'OPEN'
        self.r_status = ''
        self.save()
        e = Events.objects.create(
            status="OPEN",
            event_date_time=timezone.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment="<b>Reopened</b><br />\n%s" % comment,
            add_date_time=timezone.now())

    def reassign(self, user, assigned_to, comment):
        self.assigned_to = assigned_to
        self.assigned_user = assigned_to.user
        self.save()
        e = Events.objects.create(
            status="OPEN",
            event_date_time=timezone.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment="<b>Reassigned to %s</b><br />\n%s" % (
                assigned_to.fullname, comment),
            add_date_time=timezone.now())
        self.add_cc(assigned_to)

    def change_owner(self, user, owner, comment):
        self.owner = owner
        self.owner_user = owner.user
        self.save()
        e = Events.objects.create(
            status="OPEN",
            event_date_time=timezone.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment="<b>Ownership changed to %s</b><br />\n%s" % (
                owner.fullname, comment),
            add_date_time=timezone.now())

    def set_priority(self, priority, user):
        old_priority = self.priority
        self.priority = priority
        self.save()
        self.add_event(
            self.status,
            user,
            "<b>Priority changed from %s to %s</b>" % (
                priority_label_f(old_priority),
                priority_label_f(priority)))

    def add_event(self, status, user, comment):
        e = Events.objects.create(
            status=status,
            event_date_time=timezone.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment=comment,
            add_date_time=timezone.now())

    def setup_default_notification(self):
        self.add_cc(self.owner)
        self.add_cc(self.assigned_to)

    def add_project_notification(self):
        for u in self.milestone.project.managers():
            self.add_cc(u)

    def add_cc(self, user):
        if user.status == "inactive":
            # don't bother with inactive users
            return
        Notify.objects.get_or_create(
            item=self,
            username=user, user=user.user)

    def update_email(self, comment, user, skip_self=True):
        """Send out an email update about this PMT Item.

        When skip_self is True (which is the default), then update_email
        doesn't send an email to the passed in 'user'.
        """
        body = comment.replace(
            "<b>", "").replace("</b>", "").replace("<br />", "\n")
        body = textwrap.fill(body, replace_whitespace=False)
        # TODO: handle no user specified
        email_subj = "[PMT Item: %s] Attn: %s - %s" % (
            truncate_string(self.milestone.project.name),
            self.assigned_to.fullname,
            truncate_string(self.title))
        email_body = """
Item:\t%s
By:\t%s

Target date:\t%s
Assigned to:\t%s
Project:\t%s
Milestone:\t%s
URL:\thttps://pmt.ccnmtl.columbia.edu%s

%s


Please do not reply to this message.

""" % (
            self.title,
            user.fullname,
            self.target_date,
            self.assigned_to.fullname,
            self.milestone.project.name,
            self.milestone.name,
            self.get_absolute_url(),
            body
        )
        if skip_self:
            addresses = [u.email for u in self.users_to_email(user)]
        else:
            addresses = [u.email for u in self.users_to_email()]

        send_mail(clean_subject(email_subj), email_body, user.email,
                  addresses, fail_silently=settings.DEBUG)
        statsd.incr('main.email_sent')

    def users_to_email(self, skip=None):
        return [
            n.username
            for n in Notify.objects.filter(item=self)
            if (n.user.userprofile.status == 'active' and
                not n.user.userprofile.grp and
                n.user.userprofile != skip)]

    def copy_clients_to_new_item(self, new_item):
        for ic in self.itemclient_set.all():
            ItemClient.objects.create(item=new_item, client=ic.client)

    def clone_to_new_item(self, new_title, user):
        new_item = Item.objects.create(
            type=self.type,
            owner=self.owner,
            owner_user=self.owner.user,
            assigned_to=self.assigned_to,
            assigned_user=self.assigned_to.user,
            title=new_title,
            milestone=self.milestone,
            status='OPEN',
            r_status='',
            description='',
            priority=self.priority,
            target_date=self.target_date,
            estimated_time=self.estimated_time,
            url=self.url)
        new_item.add_event(
            'OPEN',
            user,
            (
                "<b>%s added</b>"
                "<p>Split from <a href='%s'>#%d</a></p>" % (
                    self.type, self.get_absolute_url(),
                    self.iid)))
        new_item.touch()
        new_item.setup_default_notification()
        new_item.add_project_notification()
        self.copy_clients_to_new_item(new_item)
        return new_item


def truncate_string(full_string, length=20):
    if len(full_string) > length:
        return full_string[:length] + "..."
    else:
        return full_string


def overdue_days_to_string(overdue):
    levels = [
        (-7, "ok"),
        (-1, "upcoming"),
        (1, "due"),
        (7, "overdue"),
    ]
    for days, level in levels:
        if overdue < days:
            return level
    return "late"


class HistoryItem(object):
    def __lt__(self, other):
        return self.timestamp() < other.timestamp()

    def status(self):
        return ""

    def status_class(self):
        return ""


class HistoryEvent(HistoryItem):
    def __init__(self, event):
        self.event = event

    def timestamp(self):
        return self.event.event_date_time

    def status(self):
        return self.event.status

    def status_class(self):
        return self.event.status_class()

    def _get_comment(self):
        return self.event.comment_set.first()

    def comment(self):
        return self._get_comment().comment

    def user(self):
        return UserProfile.objects.get(username=self._get_comment().username)


class HistoryComment(HistoryItem):
    def __init__(self, comment):
        self.c = comment

    def timestamp(self):
        return self.c.add_date_time

    def comment(self):
        return self.c.comment

    def user(self):
        return UserProfile.objects.get(username=self.c.username)


class Notify(models.Model):
    item = models.ForeignKey(Item,
                             null=False,
                             db_column='iid',
                             related_name='notifies')
    username = models.ForeignKey(UserProfile, db_column='username')
    user = models.ForeignKey(User)

    class Meta:
        db_table = u'notify'
        unique_together = ('item', 'username')

    def __unicode__(self):
        return '%s' % (self.user.userprofile.username)


class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    lastname = models.CharField(max_length=64, blank=True)
    firstname = models.CharField(max_length=64, blank=True)
    title = models.CharField(max_length=128, blank=True)
    registration_date = models.DateField(null=True, blank=True)
    department = models.CharField(max_length=255, blank=True)
    school = models.CharField(max_length=255, blank=True)
    add_affiliation = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.CharField(max_length=128, blank=True)
    contact = models.ForeignKey(UserProfile, null=True, db_column='contact',
                                blank=True)
    user = models.ForeignKey(User)
    comments = models.TextField(blank=True)
    status = models.CharField(max_length=16, blank=True)
    email_secondary = models.CharField(max_length=128, blank=True)
    phone_mobile = models.CharField(max_length=32, blank=True)
    phone_other = models.CharField(max_length=32, blank=True)
    website_url = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'clients'
        ordering = ['lastname', 'firstname']

    def active(self):
        return self.status == 'active'

    def get_absolute_url(self):
        return "/client/%d/" % self.client_id


class ItemClient(models.Model):
    item = models.ForeignKey(Item, db_column='iid')
    client = models.ForeignKey(Client)

    class Meta:
        db_table = u'item_clients'


class Node(models.Model):
    nid = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=256, blank=True)
    body = models.TextField(blank=True)
    user = models.ForeignKey(User)
    reply_to = models.IntegerField(null=True, blank=True)
    replies = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=8)
    overflow = models.BooleanField(default=False)
    added = models.DateTimeField()
    modified = models.DateTimeField()
    project = models.ForeignKey(Project, null=True, db_column='project')

    tags = TaggableManager()

    class Meta:
        db_table = u'nodes'
        ordering = ['-modified', ]

    def get_absolute_url(self):
        return "/forum/%d/" % self.nid

    def get_replies(self):
        return Node.objects.filter(reply_to=self.nid).order_by("modified")

    def add_reply(self, user, body):
        project = None
        if self.project_id != 0:
            project = self.project
        n = Node.objects.create(
            subject='Re: ' + self.subject,
            body=body,
            user=user.user,
            reply_to=self.nid,
            replies=0,
            type='comment',
            added=timezone.now(),
            modified=timezone.now(),
            project=project)
        self.replies = Node.objects.filter(reply_to=self.nid).count()
        self.save()
        self.email_reply(body, user, n)

    def email_reply(self, body, user, reply):
        if self.user.userprofile == user:
            # self-reply
            return
        body = textwrap.fill(body, replace_whitespace=False)
        subject = "[PMT Forum] %s" % reply.subject
        if self.project_id != 0 and self.project:
            subject = "[PMT Forum: %s] %s" % (self.project.name, reply.subject)
            body = "Project: %s\nAuthor: %s\nForum title: %s\n\n%s" % (
                self.project.name, user.fullname, reply.subject, body)
        body += (
            "\n\n\n-- \nThis message sent automatically by the PMT forum.\n"
            "To reply, please visit <https://pmt.ccnmtl.columbia.edu%s>\n\r"
            % (self.get_absolute_url()))

        send_mail(clean_subject(subject), body, user.email,
                  [self.user.userprofile.email], fail_silently=settings.DEBUG)
        statsd.incr('main.email_sent')

    def touch(self):
        self.modified = timezone.now()
        self.save()


class WorksOn(models.Model):
    username = models.ForeignKey(UserProfile, db_column='username')
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project, db_column='pid')
    auth = models.CharField(max_length=16)

    class Meta:
        db_table = u'works_on'


class Events(models.Model):
    eid = models.AutoField(primary_key=True)
    status = models.CharField(max_length=32)
    event_date_time = models.DateTimeField(null=True, blank=True)
    item = models.ForeignKey(Item, db_column='item')

    class Meta:
        db_table = u'events'
        ordering = ['event_date_time', ]

    def status_class(self):
        s = self.status.lower()
        if (s == 'open'):
            s = 'dmt-' + s
        return s


class InGroup(models.Model):
    grp = models.ForeignKey(UserProfile, db_column='grp',
                            related_name='group_members')
    username = models.ForeignKey(UserProfile, null=True,
                                 db_column='username', blank=True)

    @staticmethod
    def verbose_name(name):
        return re.sub(r' \(group\)$', '', name).title()

    def __unicode__(self):
        return InGroup.verbose_name(self.grp.fullname)

    class Meta:
        db_table = u'in_group'


class ProjectClient(models.Model):
    pid = models.ForeignKey(Project, db_column='pid')
    client = models.ForeignKey(Client)
    role = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'project_clients'


class ActualTime(models.Model):
    item = models.ForeignKey(Item, null=False, db_column='iid')
    resolver = models.ForeignKey(UserProfile, db_column='resolver')
    user = models.ForeignKey(User)
    actual_time = IntervalField(null=True, blank=True)
    completed = models.DateTimeField(primary_key=True)

    class Meta:
        db_table = u'actual_times'

    @staticmethod
    def interval_total_time(start, end):
        cursor = connection.cursor()
        cursor.execute("""
SELECT SUM(a.actual_time) AS total
FROM actual_times a, in_group g, users u
WHERE a.user_id = u.user_id AND g.username = u.username
    AND g.grp IN ('grp_programmers','grp_webmasters','grp_video',
'grp_educationaltechnologists','grp_management')
    AND a.completed > %s
    AND a.completed <= %s
        """, [start, end])
        row = cursor.fetchone()
        time = row[0]
        return time if time else timedelta(0)


class Attachment(models.Model):
    item = models.ForeignKey(Item, db_column='item_id')
    filename = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=8, blank=True)
    url = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    author = models.ForeignKey(UserProfile, db_column='author')
    user = models.ForeignKey(User, null=True)
    last_mod = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'attachment'

    def image(self):
        return self.type in ("jpg", "png", "gif")

    def get_absolute_url(self):
        return "/attachment/%d/" % self.id

    def src(self):
        # really have to think through all of this,
        # particularly on how to work attachments while
        # both the PMT and DMT exist. The PMT's approach
        # needs to die in a fire, but cutting over
        # will be tricky
        return ""


class Comment(models.Model):
    cid = models.AutoField(primary_key=True)
    comment_src = models.TextField(blank=True)
    comment = models.TextField()
    add_date_time = models.DateTimeField(null=True, blank=True)
    username = models.CharField(max_length=32)
    item = models.ForeignKey(Item, null=True, db_column='item', blank=True)
    event = models.ForeignKey(Events, null=True, db_column='event', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = u'comments'
        ordering = ['add_date_time', ]

    def user(self):
        return UserProfile.objects.get(username=self.username)

    def user_is_owner(self, user):
        """Return True if user is comment owner."""
        return self.username == user.username

    def has_been_edited(self):
        """Return True if the comment has been edited."""
        if self.created_at and self.updated_at:
            five_seconds = timedelta(seconds=5)
            # Is updated_at within 5 seconds of created_at?
            # If so, this comment probably hasn't been edited.
            if (self.updated_at + five_seconds) > self.created_at and \
               (self.updated_at - five_seconds) < self.created_at:
                return False
            else:
                return True

        return False


class StatusUpdate(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(UserProfile)
    author = models.ForeignKey(User, null=True)
    added = models.DateTimeField(auto_now_add=True)
    body = models.TextField(blank=True, default=u"")

    class Meta:
        ordering = ['-added']

    def get_absolute_url(self):
        return "/status/%d/" % self.id

    def __unicode__(self):
        return "%s - %s" % (self.project.name, self.user.fullname)

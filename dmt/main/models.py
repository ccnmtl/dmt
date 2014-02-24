from django.db import models
from datetime import timedelta, datetime
from interval.fields import IntervalField
from taggit.managers import TaggableManager


class User(models.Model):
    username = models.CharField(max_length=32, primary_key=True)
    fullname = models.CharField(max_length=128, blank=True)
    email = models.CharField(max_length=32)
    status = models.CharField(max_length=16, blank=True)
    grp = models.BooleanField(default=False)
    password = models.CharField(max_length=256, blank=True)
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

    class Meta:
        db_table = u'users'
        ordering = ['fullname']

    def __unicode__(self):
        return self.fullname

    def get_absolute_url(self):
        return "/user/%s/" % self.username

    def active(self):
        return self.status == 'active'

    def active_projects(self, start, end):
        return set(a.item.milestone.project
                   for a in self.resolve_times_for_interval(start, end))

    def has_recent_active_projects(self):
        now = datetime.today()
        start = now - timedelta(weeks=5)
        return self.actualtime_set.filter(
            completed__gte=start, completed__lte=now).count() > 0

    def recent_active_projects(self):
        """ any projects touched in the last year """
        now = datetime.today()
        start = now - timedelta(weeks=5)
        projects = Project.objects.raw(
            'SELECT distinct m.pid as pid '
            'FROM milestones m, items i, actual_times a '
            'WHERE m.mid = i.mid AND i.iid = a.iid '
            'AND a.resolver = %s '
            'AND a.completed > %s '
            'AND a.completed < %s', [self.username, start, now])
        return sorted(set(list(projects)), key=lambda x: x.name.lower())

    def resolve_times_for_interval(self, start, end):
        return ActualTime.objects.filter(
            resolver=self,
            completed__gt=start.date,
            completed__lte=end.date)

    def interval_time(self, start, end):
        return interval_sum(
            [
                a.actual_time
                for a in self.resolve_times_for_interval(start, end)])

    def weekly_report(self, week_start, week_end):
        active_projects = self.active_projects(week_start, week_end)
        # google pie chart needs max
        max_time = timedelta()
        total_time = timedelta()
        for project in active_projects:
            pu = ProjectUser(project, self)
            ptime = pu.completed_time_for_interval(week_start, week_end)
            if ptime > max_time:
                max_time = ptime
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
            ).exclude(milestone__name='Someday/Maybe')

    def resolved_owned_items(self):
        return Item.objects.filter(
            owner=self,
            status='RESOLVED'
            )

    def items(self):
        assigned = set(self.open_assigned_items())
        owned = set(self.resolved_owned_items())
        return list(assigned.union(owned))

    def clients(self):
        return Client.objects.filter(contact=self)

    def manager_on(self):
        return [w.project for w in self.workson_set.filter(auth='manager')]

    def developer_on(self):
        return [w.project for w in self.workson_set.filter(auth='developer')]

    def guest_on(self):
        return [w.project for w in self.workson_set.filter(auth='guest')]

    def total_group_time(self, start, end):
        return interval_sum(
            [u.interval_time(start, end) for u in self.users_in_group()])

    def user_groups(self):
        return [ig.grp for ig in self.ingroup_set.all()]

    def users_in_group(self):
        return [ig.username for ig in self.group_members.all()]


class ProjectUser(object):
    def __init__(self, project, user):
        self.project = project
        self.user = user

    def completed_time_for_interval(self, start, end):
        return interval_sum(
            [
                a.actual_time for a in ActualTime.objects.filter(
                    resolver=self.user,
                    item__milestone__project=self.project,
                    completed__gt=start.date,
                    completed__lte=end.date)])


# before putting in the IntervalField, there were some
# weird mismatches between what postgres would return
# and what factory_boy models would return for intervals
# this function hid the difference. Now, it looks like
# it might be unecessary. can probably remove this
# and replace with a plain sum() once a little
# more testing is done
def interval_sum(intervals):
    total = timedelta()
    for a in intervals:
        total += a
    return total


class Project(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    pub_view = models.BooleanField(default=False)
    caretaker = models.ForeignKey(User, db_column='caretaker')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, blank=True)
    type = models.CharField(max_length=50, blank=True)
    area = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=255, blank=True)
    restricted = models.CharField(max_length=10, blank=True)
    approach = models.CharField(max_length=50, blank=True)
    info_url = models.CharField(max_length=255, blank=True)
    entry_rel = models.BooleanField(default=False)
    eval_url = models.CharField(max_length=255, blank=True)
    projnum = models.IntegerField(null=True, blank=True)
    scale = models.CharField(max_length=20, blank=True)
    distrib = models.CharField(max_length=20, blank=True)
    poster = models.BooleanField(default=False)
    wiki_category = models.CharField(max_length=256, blank=True)

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

    def managers(self):
        return [w.username for w in self.workson_set.filter(auth='manager')]

    def developers(self):
        return [w.username for w in self.workson_set.filter(auth='developer')]

    def guests(self):
        return [w.username for w in self.workson_set.filter(auth='guest')]

    def upcoming_milestone(self):
        # ideally, we want a milestone that is open, in the future,
        # and as close to today as possible

        r = self.milestone_set.filter(
            status='OPEN',
            target_date__gte=datetime.today())
        if r.count():
            return r.order_by('target_date')[0]
        # there aren't any upcoming open milestones, but we need
        # to return *something*, so we'll just go with the latest
        # milestone.
        return self.milestone_set.all().order_by("-target_date")[0]

    def add_todo(self, user, title):
        milestone = self.upcoming_milestone()
        item = Item.objects.create(
            milestone=milestone,
            type='action item',
            owner=user,
            assigned_to=user,
            title=title,
            priority=1,
            status='OPEN',
            r_status='',
            estimated_time='0',
            target_date=milestone.target_date,
            last_mod=datetime.now(),
            description='')
        item.add_event('OPEN', user, "<b>action item added</b>")
        milestone.update_milestone()

    def recent_forum_posts(self, count=10):
        return self.node_set.all()[:count]

    def add_node(self, subject, user, body):
        Node.objects.create(
            subject=subject,
            body=body,
            author=user,
            reply_to=0,
            replies=0,
            type='post',
            added=datetime.now(),
            modified=datetime.now(),
            project=self)


class Document(models.Model):
    did = models.IntegerField(primary_key=True)
    pid = models.ForeignKey(Project, db_column='pid')
    filename = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=8, blank=True)
    url = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=16, blank=True)
    author = models.ForeignKey(User, db_column='author')
    last_mod = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'documents'


class Milestone(models.Model):
    mid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    target_date = models.DateField()
    project = models.ForeignKey(Project, db_column='pid')
    status = models.CharField(max_length=8)
    description = models.TextField(blank=True)

    class Meta:
        db_table = u'milestones'
        ordering = ['target_date', 'name', ]

    def get_absolute_url(self):
        return "/milestone/%d/" % self.mid

    def status_class(self):
        return self.status.lower()

    def num_open_items(self):
        return self.item_set.filter(status='OPEN').count()

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

    def open_milestone(self):
        self.status = "OPEN"
        self.save()

    def target_date_passed(self):
        return self.target_date < datetime.now().date()

    def num_unclosed_items(self):
        return self.item_set.filter(
            status__in=['OPEN', 'INPROGRESS', 'RESOLVED']).count()


class Item(models.Model):
    iid = models.AutoField(primary_key=True)
    type = models.CharField(
        max_length=12,
        choices=[('bug', 'bug'), ('action item', 'action item')])
    owner = models.ForeignKey(User, db_column='owner',
                              related_name='owned_items')
    assigned_to = models.ForeignKey(User, db_column='assigned_to',
                                    related_name='assigned_items')
    title = models.CharField(max_length=255)
    milestone = models.ForeignKey(Milestone, db_column='mid')
    status = models.CharField(
        max_length=16,
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
        return self.status.lower()

    def priority_label(self):
        labels = ['ICING', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        return labels[self.priority]

    def status_display(self):
        if self.status == 'RESOLVED':
            return self.r_status
        return self.status

    def target_date_status(self):
        overdue = (datetime.now().date() - self.target_date).days
        if overdue < -7:
            return "ok"
        elif overdue < -1:
            return "upcoming"
        elif overdue < 1:
            return "due"
        elif overdue < 7:
            return "overdue"
        else:
            return "late"

    def is_bug(self):
        return self.type == "bug"

    def history(self):
        """ interleave comments and events into one stream """
        comments = [HistoryComment(c) for c in self.comment_set.all()]
        events = [HistoryEvent(e) for e in self.events_set.all()]
        merged = comments + events
        merged.sort()
        return merged

    def add_resolve_time(self, user, time):
        completed = datetime.now()
        ActualTime.objects.create(
            item=self,
            resolver=user,
            actual_time=time,
            completed=completed)

    def add_clients(self, clients):
        # TODO: implement this
        pass

    def resolvable(self):
        return self.status in ['OPEN', 'INPROGRESS', 'NEW']

    def inprogressable(self):
        return self.status == 'OPEN'

    def verifiable(self):
        return self.status == 'RESOLVED'

    def reopenable(self):
        return self.status in ['RESOLVED', 'INPROGRESS', 'VERIFIED', 'CLOSED']

    def touch(self):
        self.last_mod = datetime.now()
        self.save()

    def add_comment(self, user, body):
        Comment.objects.create(
            item=self,
            username=user.username,
            comment=body,
            add_date_time=datetime.now())

    def resolve(self, user, r_status, comment):
        self.status = "RESOLVED"
        self.r_status = r_status
        self.save()
        e = Events.objects.create(
            status="RESOLVED",
            event_date_time=datetime.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment="<b>resolved %s</b><br />\n%s" % (r_status, comment),
            add_date_time=datetime.now())

    def verify(self, user, comment):
        self.status = 'VERIFIED'
        self.r_status = ''
        self.save()
        e = Events.objects.create(
            status="VERIFIED",
            event_date_time=datetime.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment="<b>verified</b><br />\n%s" % comment,
            add_date_time=datetime.now())

    def mark_in_progress(self, user, comment):
        self.status = 'INPROGRESS'
        self.r_status = ''
        self.save()
        e = Events.objects.create(
            status="INPROGRESS",
            event_date_time=datetime.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment="<b>marked as in progress</b><br />\n%s" % comment,
            add_date_time=datetime.now())

    def reopen(self, user, comment):
        self.status = 'OPEN'
        self.r_status = ''
        self.save()
        e = Events.objects.create(
            status="OPEN",
            event_date_time=datetime.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment="<b>reopened</b><br />\n%s" % comment,
            add_date_time=datetime.now())

    def add_event(self, status, user, comment):
        e = Events.objects.create(
            status=status,
            event_date_time=datetime.now(),
            item=self)
        Comment.objects.create(
            event=e,
            username=user.username,
            comment=comment,
            add_date_time=datetime.now())

    def setup_default_notification(self):
        self.add_cc(self.owner)
        self.add_cc(self.assigned_to)

    def add_project_notification(self):
        for n in NotifyProject.objects.filter(pid=self.milestone.project):
            self.add_cc(n.username)

    def add_cc(self, user):
        if user.status == "inactive":
            # don't bother with inactive users
            return
        Notify.objects.get_or_create(
            item=self,
            username=user)


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
        r = self.event.comment_set.all()
        if r.count():
            return r[0]
        return None

    def comment(self):
        return self._get_comment().comment

    def user(self):
        return User.objects.get(username=self._get_comment().username)


class HistoryComment(HistoryItem):
    def __init__(self, comment):
        self.c = comment

    def timestamp(self):
        return self.c.add_date_time

    def comment(self):
        return self.c.comment

    def user(self):
        return User.objects.get(username=self.c.username)


class Notify(models.Model):
    item = models.ForeignKey(Item, null=False, db_column='iid')
    username = models.ForeignKey(User, db_column='username')

    class Meta:
        db_table = u'notify'


class Client(models.Model):
    client_id = models.IntegerField(primary_key=True)
    lastname = models.CharField(max_length=64, blank=True)
    firstname = models.CharField(max_length=64, blank=True)
    title = models.CharField(max_length=128, blank=True)
    registration_date = models.DateField(null=True, blank=True)
    department = models.CharField(max_length=255, blank=True)
    school = models.CharField(max_length=255, blank=True)
    add_affiliation = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.CharField(max_length=128, blank=True)
    contact = models.ForeignKey(User, null=True, db_column='contact',
                                blank=True)
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


class ItemClient(models.Model):
    item = models.ForeignKey(Item, db_column='iid')
    client = models.ForeignKey(Client)

    class Meta:
        db_table = u'item_clients'


class Node(models.Model):
    nid = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=256, blank=True)
    body = models.TextField(blank=True)
    author = models.ForeignKey(User, db_column='author')
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
        Node.objects.create(
            subject='Re: ' + self.subject,
            body=body,
            author=user,
            reply_to=self.nid,
            replies=0,
            type='comment',
            added=datetime.now(),
            modified=datetime.now(),
            project=self.project)
        self.replies = Node.objects.filter(reply_to=self.nid).count()
        self.save()

    def touch(self):
        self.modified = datetime.now()
        self.save()


class WorksOn(models.Model):
    username = models.ForeignKey(User, db_column='username')
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
        return self.status.lower()


class NotifyProject(models.Model):
    pid = models.ForeignKey(Project, db_column='pid')
    username = models.ForeignKey(User, db_column='username')

    class Meta:
        db_table = u'notify_project'


class InGroup(models.Model):
    grp = models.ForeignKey(User, db_column='grp',
                            related_name='group_members')
    username = models.ForeignKey(User, null=True,
                                 db_column='username', blank=True)

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
    resolver = models.ForeignKey(User, db_column='resolver')
    actual_time = IntervalField(null=True, blank=True)
    completed = models.DateTimeField(primary_key=True)

    class Meta:
        db_table = u'actual_times'


class Attachment(models.Model):
    item = models.ForeignKey(Item, db_column='item_id')
    filename = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=8, blank=True)
    url = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    author = models.ForeignKey(User, db_column='author')
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
    comment = models.TextField()
    add_date_time = models.DateTimeField(null=True, blank=True)
    username = models.CharField(max_length=32)
    item = models.ForeignKey(Item, null=True, db_column='item', blank=True)
    event = models.ForeignKey(Events, null=True, db_column='event', blank=True)

    class Meta:
        db_table = u'comments'
        ordering = ['add_date_time', ]

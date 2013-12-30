from django.db import models
from datetime import timedelta


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

    def resolve_times_for_interval(self, start, end):
        return ActualTime.objects.filter(
            resolver=self,
            completed__gt=start.date,
            completed__lte=end.date)

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


class ProjectUser(object):
    def __init__(self, project, user):
        self.project = project
        self.user = user

    def completed_time_for_interval(self, start, end):
        total = timedelta()
        for a in ActualTime.objects.filter(
                resolver=self.user,
                item__milestone__project=self.project,
                completed__gt=start.date,
                completed__lte=end.date):
            if isinstance(a.actual_time, timedelta):
                total += a.actual_time
            else:
                # intervals from the database always come in as
                # timedelta's but factory_boy seems to make
                # them floats, so we need to be able to handle
                # both...
                total += timedelta(a.actual_time)
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


class Item(models.Model):
    iid = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=12)
    owner = models.ForeignKey(User, db_column='owner',
                              related_name='owned_items')
    assigned_to = models.ForeignKey(User, db_column='assigned_to',
                                    related_name='assigned_items')
    title = models.CharField(max_length=255)
    milestone = models.ForeignKey(Milestone, db_column='mid')
    status = models.CharField(max_length=16)
    description = models.TextField(blank=True)
    priority = models.IntegerField(null=True, blank=True)
    r_status = models.CharField(max_length=16, blank=True)
    last_mod = models.DateTimeField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    estimated_time = models.TextField(blank=True)
    url = models.TextField(blank=True)

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

    def is_bug(self):
        return self.type == "bug"

    def history(self):
        """ interleave comments and events into one stream """
        comments = [HistoryComment(c) for c in self.comment_set.all()]
        events = [HistoryEvent(e) for e in self.events_set.all()]
        merged = comments + events
        merged.sort()
        return merged


class HistoryItem(object):
    def __lt__(self, other):
        return self.timestamp() < other.timestamp()

    def status(self):
        return ""


class HistoryEvent(HistoryItem):
    def __init__(self, event):
        self.event = event

    def timestamp(self):
        return self.event.event_date_time

    def status(self):
        return self.event.status

    def _get_comment(self):
        r = self.event.comment_set.all()
        if r.count():
            return r[0]
        return None

    def comment(self):
        return self._get_comment().comment

    def user(self):
        return self._get_comment().username


class HistoryComment(HistoryItem):
    def __init__(self, comment):
        self.c = comment

    def timestamp(self):
        return self.c.add_date_time

    def comment(self):
        return self.c.comment

    def user(self):
        return self.c.username


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


class ItemClient(models.Model):
    item = models.ForeignKey(Item, db_column='iid')
    client = models.ForeignKey(Client)

    class Meta:
        db_table = u'item_clients'


class Node(models.Model):
    nid = models.IntegerField(primary_key=True)
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

    class Meta:
        db_table = u'nodes'
        ordering = ['-modified', ]

    def get_absolute_url(self):
        return "/forum/%d/" % self.nid


class WorksOn(models.Model):
    username = models.ForeignKey(User, db_column='username')
    project = models.ForeignKey(Project, db_column='pid')
    auth = models.CharField(max_length=16)

    class Meta:
        db_table = u'works_on'


class Events(models.Model):
    eid = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=32)
    event_date_time = models.DateTimeField(null=True, blank=True)
    item = models.ForeignKey(Item, db_column='item')

    class Meta:
        db_table = u'events'
        ordering = ['event_date_time', ]


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
    actual_time = models.FloatField(null=True, blank=True)
    completed = models.DateTimeField(primary_key=True)

    class Meta:
        db_table = u'actual_times'


class Attachment(models.Model):
    item = models.ForeignKey(Item, db_column='iid')
    filename = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=8, blank=True)
    url = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    author = models.ForeignKey(User, db_column='author')
    last_mod = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'attachment'


class Comment(models.Model):
    cid = models.IntegerField(primary_key=True)
    comment = models.TextField()
    add_date_time = models.DateTimeField(null=True, blank=True)
    username = models.CharField(max_length=32)
    item = models.ForeignKey(Item, null=True, db_column='item', blank=True)
    event = models.ForeignKey(Events, null=True, db_column='event', blank=True)

    class Meta:
        db_table = u'comments'
        ordering = ['add_date_time', ]

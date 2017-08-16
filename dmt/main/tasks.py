import pytz
import random
import smtplib
import time
from celery.decorators import periodic_task, task
from celery.task.schedules import crontab
from django.conf import settings
from django.core.mail import send_mail
from django.db import connection
from django.utils import timezone
from django_statsd.clients import statsd
from datetime import datetime, timedelta
from pytz import AmbiguousTimeError


def exp_backoff(tries):
    """ exponential backoff with jitter

    back off 2^1, then 2^2, 2^3 (seconds), etc.

    add a 10% jitter to prevent thundering herd.

    """
    backoff = 2 ** tries
    jitter = random.uniform(0, backoff * .1)  # nosec
    return int(backoff + jitter)


def get_item_counts_by_status():
    from .models import Item
    data = dict()
    data['total'] = Item.objects.count()
    data['open'] = Item.objects.filter(status='OPEN').count()
    data['inprogress'] = Item.objects.filter(status='INPROGRESS').count()
    data['resolved'] = Item.objects.filter(status='RESOLVED').count()
    data['closed'] = Item.objects.filter(status='CLOSED').count()
    data['verified'] = Item.objects.filter(status='VERIFIED').count()
    return data


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def item_stats_report():
    start = time.time()
    d = get_item_counts_by_status()
    statsd.gauge("items.total", d['total'])
    statsd.gauge("items.open", d['open'])
    statsd.gauge("items.inprogress", d['inprogress'])
    statsd.gauge("items.resolved", d['resolved'])
    statsd.gauge("items.closed", d['closed'])
    statsd.gauge("items.verified", d['verified'])
    end = time.time()
    statsd.timing('celery.item_stats_report', int((end - start) * 1000))


def item_counts():
    from .models import Item, interval_sum
    d = dict()
    d['total_open_items'] = Item.objects.filter(
        status__in=['OPEN', 'INPROGRESS'])
    d['open_sm_items'] = Item.objects.filter(
        status__in=['OPEN', 'INPROGRESS'],
        milestone__name='Someday/Maybe')
    d['open_sm_count'] = d['total_open_items'].count()
    total_hours_estimated = interval_sum(
        [i.estimated_time for i in d['total_open_items']]
    ).total_seconds() / 3600.

    sm_hours_estimated = interval_sum(
        [i.estimated_time for i in d['open_sm_items']]
    ).total_seconds() / 3600.

    d['estimates_sm'] = int(sm_hours_estimated)
    d['estimates_non_sm'] = int(
        total_hours_estimated - sm_hours_estimated)
    return d


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def estimates_report():
    start = time.time()
    d = item_counts()
    # item counts
    statsd.gauge('items.open.sm', d['open_sm_count'])

    # hour estimates
    statsd.gauge('estimates.sm', d['estimates_sm'])
    statsd.gauge('estimates.non_sm', d['estimates_non_sm'])

    end = time.time()
    statsd.timing('celery.estimates_report', int((end - start) * 1000))


def hours_logged(weeks=1):
    from .models import ActualTime, interval_sum
    now = timezone.now()
    one_week_ago = now - timedelta(weeks=weeks)
    # active projects
    try:
        times_logged = ActualTime.objects.filter(
            completed__gt=one_week_ago).select_related(
            'item', 'user', 'item__milestone',
            'item__milestone__project')
        return int(
            interval_sum(
                [a.actual_time for a in times_logged]
            ).total_seconds() / 3600.)
    except AmbiguousTimeError:
        # once a year, for an hour, exactly one week after DST changes,
        # the one_week_ago time refers to the period of time
        # that "existed" twice. We *could* fudge things by an hour,
        # but for the sake of making hourly log graphs, it's simpler
        # to just punt and log '0' for a bit.
        return 0


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def hours_logged_report():
    start = time.time()
    statsd.gauge("hours.one_week", hours_logged())
    end = time.time()
    statsd.timing('celery.hours_logged_report', int((end - start) * 1000))


def seconds_to_hours(seconds):
    return seconds / 3600.


# NOTE: these functions aren't really testable
# the SQL is postgresql-only (since it uses PG's 'interval' datatype)
# and breaks in SQLite. If you change them, be extra careful.
def total_hours_logged_by_project():
    q = """SELECT m.pid, extract ('epoch' from sum(a.actual_time)::interval)
           FROM actual_times a, items i, milestones m
           WHERE a.iid = i.iid
             AND i.mid = m.mid GROUP BY m.pid;"""
    cursor = connection.cursor()
    cursor.execute(q)
    for (pid, seconds) in cursor.fetchall():
        yield (pid, seconds_to_hours(seconds))


def total_hours_estimated_by_project():
    q = """SELECT m.pid, extract ('epoch' from sum(i.estimated_time)::interval)
           FROM items i, milestones m
           WHERE i.status in ('OPEN', 'INPROGRESS')
             AND i.mid = m.mid GROUP BY m.pid;"""
    cursor = connection.cursor()
    cursor.execute(q)
    for (pid, seconds) in cursor.fetchall():
        yield (pid, seconds_to_hours(seconds))


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def total_hours_estimated_vs_logged():
    for pid, hours in total_hours_estimated_by_project():
        statsd.gauge("projects.%d.hours_estimated" % pid, int(hours))
    for pid, hours in total_hours_logged_by_project():
        statsd.gauge("projects.%d.hours_logged" % pid, int(hours))


@periodic_task(run_every=crontab(hour=1, minute=0, day_of_week='*'))
def close_passed_milestones():
    from .models import Milestone
    now = timezone.now()
    for milestone in Milestone.objects.filter(
            status='OPEN', target_date__lt=now):
        milestone.update_milestone()


@periodic_task(run_every=crontab(hour=12, minute=0, day_of_week='fri'))
def weekly_report_emails():
    from .models import UserProfile
    for user in UserProfile.objects.filter(status='active', grp=False):
        user_weekly_report_email.delay(username=user.username)


@task
def user_weekly_report_email(username):
    from .models import UserProfile
    u = UserProfile.objects.get(username=username)
    u.send_weekly_report()


@task
def reminder_email(reminder):
    up = reminder.user.userprofile
    up.send_reminder(reminder)
    reminder.delete()


@periodic_task(run_every=crontab(minute=0, hour='*'))
def send_reminder_emails():
    """Email any reminders to users that have set them up.

    Users can set up action items to automatically remind themselves
    before the due date ahead of time. The granularity is hourly, so
    this task is set up to run every hour.
    """
    # Find all reminders where the item has a target date,
    # and the user is active, and the item is not verified.
    from .models import Reminder
    reminders = Reminder.objects.filter(
        item__target_date__isnull=False,
        user__is_active=True
    ).exclude(item__status__in=['VERIFIED', 'RESOLVED'])

    now = timezone.now()
    five_mins = timedelta(minutes=5)

    for r in reminders:
        # Find out if this reminder is ready to be sent.
        target_datetime = datetime.combine(
            r.item.target_date, datetime.min.time())
        aware_target = pytz.timezone(settings.TIME_ZONE).localize(
            target_datetime)
        if ((aware_target - r.reminder_time) < (now + five_mins)):
            reminder_email.delay(reminder=r)


@periodic_task(run_every=crontab(hour=0, minute=0))
def bump_someday_maybe_target_dates():

    """Someday/Maybe milestones are "special" and should never actually
    reach a target date.  so once a day, we take any that are upcoming
    and push them far into the future again.

    They should also never be the next upcoming milestone on a project
    unless that project doesn't have any other milestones.
    """

    from .models import Milestone, Project
    now = timezone.now()
    upcoming = now + timedelta(weeks=4)
    future = now + timedelta(weeks=52)
    for m in Milestone.objects.filter(
            name="Someday/Maybe",
            target_date__lt=upcoming,
            status='OPEN'):
        m.target_date = future.date()
        m.save()
    for p in Project.objects.all():
        p.ensure_someday_maybe_is_furthest()


@task(ignore_results=True, bind=True, max_retries=None)
def send_email(self, subject, body, to_addresses):
    try:
        send_mail(
            subject,
            body, settings.SERVER_EMAIL,
            to_addresses, fail_silently=settings.DEBUG)
    except (smtplib.SMTPAuthenticationError,
            smtplib.SMTPServerDisconnected,
            smtplib.SMTPConnectError,
            smtplib.SMTPDataError) as exc:
        if self.request.retries > settings.EMAIL_MAX_RETRIES:
            raise exc
        else:
            self.retry(exc=exc, countdown=exp_backoff(self.request.retries))

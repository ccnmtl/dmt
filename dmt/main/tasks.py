from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.db import connection
from django_statsd.clients import statsd
from datetime import datetime, timedelta
import time
from .models import Item, ActualTime, interval_sum
from .models import User, Milestone
from dmt.claim.models import Claim


def get_item_counts_by_status():
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
    now = datetime.now()
    one_week_ago = now - timedelta(weeks=weeks)
    # active projects
    times_logged = ActualTime.objects.filter(
        completed__gt=one_week_ago).select_related(
        'item', 'resolver', 'item__milestone',
        'item__milestone__project')
    return int(
        interval_sum(
            [a.actual_time for a in times_logged]
        ).total_seconds() / 3600.)


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def hours_logged_report():
    start = time.time()
    statsd.gauge("hours.one_week", hours_logged())
    end = time.time()
    statsd.timing('celery.hours_logged_report', int((end - start) * 1000))


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def user_stats():
    active_users = User.objects.filter(status='active', grp=False).count()
    claimed = Claim.objects.all().count()
    statsd.gauge('users.active', active_users)
    statsd.gauge('users.claimed', claimed)


def seconds_to_hours(seconds):
    return seconds / 3600.


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
           WHERE i.status = 'OPEN'
             AND i.mid = m.mid GROUP BY m.pid;"""
    cursor = connection.cursor()
    cursor.execute(q)
    for (pid, seconds) in cursor.fetchall():
        yield (pid, seconds_to_hours(seconds))


def total_hours_logged_by_milestone():
    q = """SELECT i.mid, extract ('epoch' from sum(a.actual_time)::interval)
           FROM actual_times a, items i
           WHERE a.iid = i.iid
           GROUP BY i.mid;"""
    cursor = connection.cursor()
    cursor.execute(q)
    for (mid, seconds) in cursor.fetchall():
        yield (mid, seconds_to_hours(seconds))


def total_hours_estimated_by_milestone():
    q = """SELECT i.mid, extract ('epoch' from sum(i.estimated_time)::interval)
           FROM items i
           WHERE i.status = 'OPEN'
           GROUP BY i.mid;"""
    cursor = connection.cursor()
    cursor.execute(q)
    for (mid, seconds) in cursor.fetchall():
        yield (mid, seconds_to_hours(seconds))


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def total_hours_estimated_vs_logged():
    for pid, hours in total_hours_estimated_by_project():
        statsd.gauge("projects.%d.hours_estimated" % pid, int(hours))
    for pid, hours in total_hours_logged_by_project():
        statsd.gauge("projects.%d.hours_logged" % pid, int(hours))

    for mid, hours in total_hours_estimated_by_milestone():
        statsd.gauge("milestones.%d.hours_estimated" % mid, int(hours))
    for mid, hours in total_hours_logged_by_milestone():
        statsd.gauge("milestones.%d.hours_logged" % mid, int(hours))


@periodic_task(run_every=crontab(hour=1, minute=0, day_of_week='*'))
def close_passed_milestones():
    now = datetime.now()
    for milestone in Milestone.objects.filter(
            status='OPEN', target_date__lt=now):
        milestone.update_milestone()

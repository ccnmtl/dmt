from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django_statsd.clients import statsd
from datetime import datetime, timedelta
import time
from .models import Item, ActualTime, interval_sum
from .models import User
from dmt.claim.models import Claim


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def item_stats_report():
    start = time.time()
    statsd.gauge("items.total", Item.objects.count())
    statsd.gauge("items.open", Item.objects.filter(status='OPEN').count())
    statsd.gauge("items.inprogress",
                 Item.objects.filter(status='INPROGRESS').count())
    statsd.gauge("items.resolved",
                 Item.objects.filter(status='RESOLVED').count())
    statsd.gauge("items.closed",
                 Item.objects.filter(status='CLOSED').count())
    statsd.gauge("items.verified",
                 Item.objects.filter(status='VERIFIED').count())
    end = time.time()
    statsd.timing('celery.item_stats_report', int((end - start) * 1000))


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def estimates_report():
    start = time.time()
    total_open_items = Item.objects.filter(
        status__in=['OPEN', 'INPROGRESS'])
    open_sm_items = Item.objects.filter(
        status__in=['OPEN', 'INPROGRESS'],
        milestone__name='Someday/Maybe')
    # item counts
    statsd.gauge('items.open.sm', open_sm_items.count())

    # hour estimates
    total_hours_estimated = interval_sum(
        [i.estimated_time for i in total_open_items]
    ).total_seconds() / 3600.

    sm_hours_estimated = interval_sum(
        [i.estimated_time for i in open_sm_items]
    ).total_seconds() / 3600.

    statsd.gauge('estimates.sm', int(sm_hours_estimated))
    statsd.gauge('estimates.non_sm',
                 int(total_hours_estimated - sm_hours_estimated))

    end = time.time()
    statsd.timing('celery.estimates_report', int((end - start) * 1000))


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def hours_logged_report():
    start = time.time()
    now = datetime.now()
    one_week_ago = now - timedelta(weeks=1)
    # active projects
    times_logged = ActualTime.objects.filter(
        completed__gt=one_week_ago).select_related(
        'item', 'resolver', 'item__milestone',
        'item__milestone__project')
    statsd.gauge(
        "hours.one_week",
        int(
            interval_sum(
                [a.actual_time for a in times_logged]
            ).total_seconds() / 3600.))
    end = time.time()
    statsd.timing('celery.hours_logged_report', int((end - start) * 1000))


@periodic_task(run_every=crontab(hour='*', minute='*', day_of_week='*'))
def user_stats():
    active_users = User.objects.filter(status='active', grp=False).count()
    claimed = Claim.objects.all().count()
    statsd.gauge('users.active', active_users)
    statsd.gauge('users.claimed', claimed)

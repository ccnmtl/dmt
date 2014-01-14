from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from dmt.main.models import User
from datetime import datetime, timedelta


class UserWeeklyView(TemplateView):
    template_name = "report/user_weekly.html"

    def get_context_data(self, **kwargs):
        username = kwargs['pk']
        user = get_object_or_404(User, username=username)
        now = datetime.today()
        if self.request.GET.get('date', None):
            (y, m, d) = self.request.GET['date'].split('-')
            now = datetime(year=int(y), month=int(m), day=int(d))
        week_start = now + timedelta(days=-now.weekday())
        week_end = week_start + timedelta(days=6)
        prev_week = week_start - timedelta(weeks=1)
        next_week = week_start + timedelta(weeks=1)
        data = user.weekly_report(week_start, week_end)
        data.update(dict(u=user, now=now,
                         week_start=week_start.date,
                         week_end=week_end.date,
                         prev_week=prev_week.date,
                         next_week=next_week.date,
                         ))
        return data


class StaffReportView(TemplateView):
    template_name = "report/staff_report.html"

    def get_context_data(self, **kwargs):
        now = datetime.today()
        if self.request.GET.get('date', None):
            (y, m, d) = self.request.GET['date'].split('-')
            now = datetime(year=int(y), month=int(m), day=int(d))
        week_start = now + timedelta(days=-now.weekday())
        week_end = week_start + timedelta(days=6)
        prev_week = week_start - timedelta(weeks=1)
        next_week = week_start + timedelta(weeks=1)
        data = staff_report_data(week_start, week_end)
        data.update(dict(now=now,
                         week_start=week_start.date,
                         week_end=week_end.date,
                         prev_week=prev_week.date,
                         next_week=next_week.date,
                         ))
        return data


def staff_report_data(start, end):
    groups = ['programmers', 'video', 'webmasters', 'educationaltechnologists',
              'management']
    group_reports = []

    for grp in groups:
        try:
            group_user = User.objects.get(username="grp_" + grp)
        except User.DoesNotExist:
            continue
        group_total_time = group_user.total_group_time(start, end)
        data = dict(group=group_user, total_time=group_total_time)
        user_data = []
        for user in group_user.users_in_group():
            user_time = user.interval_time(start, end)
            user_data.append(dict(user=user, user_time=user_time))
        data['user_data'] = user_data
        data['max_time'] = max(u['user_time'] for u in user_data)
        group_reports.append(data)

    group_max_time = max([g['total_time'] for g in group_reports])
    return dict(groups=group_reports, group_max_time=group_max_time)

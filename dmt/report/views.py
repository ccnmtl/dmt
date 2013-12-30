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

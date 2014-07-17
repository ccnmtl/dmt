from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View
from dmt.claim.models import Claim
from dmt.main.models import User, Item
from dmt.main.views import LoggedInMixin
from .models import StaffReportCalculator, WeeklySummaryReportCalculator
from .mixins import PrevNextWeekMixin


class YearlyReviewView(LoggedInMixin, View):
    def get(self, request):
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        return HttpResponseRedirect("/report/user/%s/yearly/" % user.username)


class UserYearlyView(LoggedInMixin, TemplateView):
    template_name = "report/user_yearly.html"

    def get_context_data(self, **kwargs):
        context = super(UserYearlyView, self).get_context_data(**kwargs)
        username = kwargs['pk']
        user = get_object_or_404(User, username=username)
        now = datetime.today()
        interval_start = now + timedelta(days=-365)
        interval_end = now
        data = user.weekly_report(interval_start, interval_end)
        data.update(dict(u=user, now=now,
                         interval_start=interval_start.date,
                         interval_end=interval_end.date,
                         ))
        context.update(data)
        return context


class UserWeeklyView(LoggedInMixin, PrevNextWeekMixin, TemplateView):
    template_name = "report/user_weekly.html"

    def get_context_data(self, **kwargs):
        context = super(UserWeeklyView, self).get_context_data(**kwargs)
        username = kwargs['pk']
        user = get_object_or_404(User, username=username)
        data = user.weekly_report(self.week_start, self.week_end)
        data.update(dict(u=user, now=self.now,
                         week_start=self.week_start.date,
                         week_end=self.week_end.date,
                         prev_week=self.prev_week.date,
                         next_week=self.next_week.date,
                         ))
        context.update(data)
        return context


class StaffReportPreviousWeekView(LoggedInMixin, PrevNextWeekMixin, View):
    def get(self, request, **kwargs):
        return HttpResponseRedirect(
            "/report/staff/?date=%04d-%02d-%02d" % (
                self.prev_week.year, self.prev_week.month, self.prev_week.day))


class StaffReportView(LoggedInMixin, PrevNextWeekMixin, TemplateView):
    template_name = "report/staff_report.html"

    def get_context_data(self, **kwargs):
        context = super(StaffReportView, self).get_context_data(**kwargs)
        report = StaffReportCalculator(['programmers', 'video', 'webmasters',
                                        'educationaltechnologists',
                                        'management'])
        data = report.calc(self.week_start, self.week_end)
        data.update(dict(now=self.now,
                         week_start=self.week_start.date,
                         week_end=self.week_end.date,
                         prev_week=self.prev_week.date,
                         next_week=self.next_week.date,
                         ))
        context.update(data)
        return context


class WeeklySummaryView(LoggedInMixin, PrevNextWeekMixin, TemplateView):
    template_name = 'report/weekly_summary.html'

    def get_context_data(self, **kwargs):
        context = super(WeeklySummaryView, self).get_context_data(**kwargs)

        report = WeeklySummaryReportCalculator(['programmers', 'webmasters',
                                                'educationaltechnologists',
                                                'video', 'management'])
        data = report.calc(self.week_start, self.week_end)
        context.update(data)

        context.update(dict(now=self.now,
                            week_start=self.week_start.date,
                            week_end=self.week_end.date,
                            prev_week=self.prev_week.date,
                            next_week=self.next_week.date))
        return context


class ResolvedView(LoggedInMixin, TemplateView):
    template_name = "report/resolved.html"

    def get_context_data(self, **kwargs):
        context = super(ResolvedView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.filter(status='RESOLVED')
        return context

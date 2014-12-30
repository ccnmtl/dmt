from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View
from dmt.claim.models import Claim
from dmt.main.models import UserProfile, Item, Milestone, Project
from dmt.main.views import LoggedInMixin
from dmt.main.utils import interval_to_hours
from .models import (
    ActiveProjectsCalculator, StaffReportCalculator,
    WeeklySummaryReportCalculator)
from .mixins import PrevNextWeekMixin
from .utils import ReportFileGenerator


class ProjectHoursView(LoggedInMixin, View):
    def get(self, request, pk):
        p = get_object_or_404(Project, pk=pk)
        actual_times = p.all_actual_times()
        filename = "project-hours-%d" % p.pid

        column_names = [
            'iid', 'item title', 'type', 'owner', 'assigned_to',
            'priority', 'target_date', 'estimated_time',
            'mid', 'milestone', 'user', 'hours', 'completed at']

        rows = [[a.item.iid, a.item.title, a.item.type,
                 a.item.owner.username, a.item.assigned_to.username,
                 a.item.priority, a.item.target_date,
                 interval_to_hours(a.item.estimated_time),
                 a.item.milestone.mid, a.item.milestone.name,
                 a.resolver.username, interval_to_hours(a.actual_time),
                 a.completed]
                for a in actual_times]

        generator = ReportFileGenerator()
        return generator.generate(
            column_names, rows, filename,
            self.request.GET.get('format', 'csv'))


class ActiveProjectsView(LoggedInMixin, TemplateView):
    template_name = "report/active_projects.html"

    def get_context_data(self, **kwargs):
        context = super(ActiveProjectsView, self).get_context_data(**kwargs)

        days = 31
        if self.request.GET.get('days', None):
            days = int(self.request.GET['days'])

        calc = ActiveProjectsCalculator()
        data = calc.calc(days)
        context.update(data)

        # Find dates for displaying to the user
        now = datetime.now()
        context['interval_start'] = now + timedelta(days=-days)
        context['interval_end'] = now

        return context


class ActiveProjectsExportView(LoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        days = 31
        if self.request.GET.get('days', None):
            days = int(self.request.GET['days'])

        calc = ActiveProjectsCalculator()
        data = calc.calc(days)

        # Find dates for displaying to the user
        now = datetime.now()
        interval_start = now + timedelta(days=-days)
        interval_end = now
        start_str = interval_start.strftime('%Y%m%d')
        end_str = interval_end.strftime('%Y%m%d')
        filename = "active-projects-%s-%s" % (start_str, end_str)

        column_names = ['ID', 'Name', 'Project Number', 'Last worked on',
                        'Project Status', 'Caretaker', 'Hours logged']

        rows = [[x.pid, x.name, x.projnum, x.last_worked_on, x.status,
                 x.caretaker, interval_to_hours(x.hours_logged)]
                for x in data['projects']]

        generator = ReportFileGenerator()
        return generator.generate(
            column_names, rows, filename, self.request.GET.get('format'))


class YearlyReviewView(LoggedInMixin, View):
    def get(self, request):
        user = get_object_or_404(Claim, django_user=request.user).pmt_user
        return HttpResponseRedirect("/report/user/%s/yearly/" % user.username)


class UserYearlyView(LoggedInMixin, TemplateView):
    template_name = "report/user_yearly.html"

    def get_context_data(self, **kwargs):
        context = super(UserYearlyView, self).get_context_data(**kwargs)
        username = kwargs['pk']
        user = get_object_or_404(UserProfile, username=username)
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
        user = get_object_or_404(UserProfile, username=username)
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
        calc = StaffReportCalculator(['designers', 'programmers', 'video',
                                      'educationaltechnologists',
                                      'management'])
        data = calc.calc(self.week_start, self.week_end)
        context.update(dict(now=self.now, now_str=self.now_str,
                            week_start=self.week_start.date,
                            week_end=self.week_end.date,
                            prev_week=self.prev_week.date,
                            prev_week_str=self.prev_week_str,
                            next_week=self.next_week.date,
                            next_week_str=self.next_week_str))
        context.update(data)
        return context


class StaffReportExportView(LoggedInMixin, PrevNextWeekMixin, View):
    def get(self, request, *args, **kwargs):
        self.get_params()

        calc = StaffReportCalculator(['designers', 'programmers', 'video',
                                      'educationaltechnologists',
                                      'management'])
        data = calc.calc(self.week_start, self.week_end)

        start_str = self.week_start.strftime('%Y%m%d')
        end_str = self.week_end.strftime('%Y%m%d')
        filename = "staff-report-%s-%s" % (start_str, end_str)

        column_names = ['Staff Member', 'Group', 'Hours Logged']

        rows = [[x['user'].fullname, x['group_name'],
                 interval_to_hours(x['user_time'])]
                for x in data['users']]

        generator = ReportFileGenerator()
        return generator.generate(
            column_names, rows, filename, self.request.GET.get('format'))


class WeeklySummaryView(LoggedInMixin, PrevNextWeekMixin, TemplateView):
    template_name = 'report/weekly_summary.html'

    def get_context_data(self, **kwargs):
        context = super(WeeklySummaryView, self).get_context_data(**kwargs)

        calc = WeeklySummaryReportCalculator(['designers', 'programmers',
                                              'educationaltechnologists',
                                              'video', 'management'])
        data = calc.calc(self.week_start, self.week_end)
        context.update(data)

        context.update(dict(now=self.now, now_str=self.now_str,
                            week_start=self.week_start.date,
                            week_end=self.week_end.date,
                            prev_week=self.prev_week.date,
                            prev_week_str=self.prev_week_str,
                            next_week=self.next_week.date,
                            next_week_str=self.next_week_str))
        return context


class WeeklySummaryExportView(LoggedInMixin, PrevNextWeekMixin, View):
    def get(self, request, **kwargs):
        self.get_params()

        groups = ['designers', 'programmers', 'educationaltechnologists',
                  'video', 'management']
        report = WeeklySummaryReportCalculator(groups)
        data = report.calc(self.week_start, self.week_end)

        start_str = self.week_start.strftime('%Y%m%d')
        end_str = self.week_end.strftime('%Y%m%d')
        filename = "weekly-summary-report-%s-%s" % (start_str, end_str)

        column_names = ['Project'] + [x.capitalize() for x in groups] + \
                       ['Project Total']

        rows = []
        for project in data['project_times']:
            row = [project['name']]

            for grouptime in project['group_times']:
                row.append(interval_to_hours(grouptime))

            row.append(interval_to_hours(project['total_time']))
            rows.append(row)

        generator = ReportFileGenerator()
        return generator.generate(
            column_names, rows, filename, self.request.GET.get('format'))


class ResolvedView(LoggedInMixin, TemplateView):
    template_name = "report/resolved.html"

    def get_context_data(self, **kwargs):
        context = super(ResolvedView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.filter(status='RESOLVED')
        return context


class PassedMilestonesView(LoggedInMixin, TemplateView):
    template_name = "report/passed_milestones.html"

    def get_context_data(self, **kwargs):
        context = super(PassedMilestonesView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.filter(status='RESOLVED')

        now = datetime.now()
        context['milestones'] = Milestone.objects.filter(
            status='OPEN',
            target_date__lt=now,
            ).order_by("target_date").select_related('project')

        return context

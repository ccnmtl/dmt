from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import TemplateView, View
import pytz

from dmt.main.mixins import DaterangeMixin
from dmt.main.models import UserProfile, Item, Milestone, Project
from dmt.main.utils import interval_to_hours
from dmt.main.views import LoggedInMixin
from dmt.report.calculators import (
    ActiveProjectsCalculator, StaffReportCalculator,
    TimeSpentByUserCalculator, TimeSpentByProjectCalculator,
    ProjectStatusCalculator, StaffCapacityCalculator
)
from dmt.report.mixins import PrevNextWeekMixin
from dmt.report.utils import ReportFileGenerator


class ProjectHoursView(LoggedInMixin, View):
    def get(self, request, pk):
        p = get_object_or_404(Project, pk=pk)

        if request.GET.get('interval_start') and \
           request.GET.get('interval_end'):
            interval_start = pytz.timezone(settings.TIME_ZONE).localize(
                datetime.combine(
                    parse_date(request.GET.get('interval_start')),
                    datetime.min.time()))
            interval_end = pytz.timezone(settings.TIME_ZONE).localize(
                datetime.combine(
                    parse_date(request.GET.get('interval_end')),
                    datetime.max.time()))
            actual_times = p.actual_times_between(interval_start, interval_end)
        else:
            actual_times = p.all_actual_times()

        filename = "project-hours-%d" % p.pid

        column_names = [
            'iid', 'item title', 'type', 'owner', 'assigned_to',
            'priority', 'target_date', 'estimated_time',
            'mid', 'milestone', 'user', 'hours', 'completed at']

        rows = [[a.item.iid, a.item.title, a.item.type,
                 a.item.owner_user.userprofile.username,
                 a.item.assigned_user.userprofile.username,
                 a.item.priority, a.item.target_date,
                 interval_to_hours(a.item.estimated_time),
                 a.item.milestone.mid, a.item.milestone.name,
                 a.user.userprofile.username, interval_to_hours(a.actual_time),
                 a.completed]
                for a in actual_times]

        generator = ReportFileGenerator()
        return generator.generate(
            column_names, rows, filename,
            self.request.GET.get('format', 'csv'))


class ActiveProjectsView(LoggedInMixin, DaterangeMixin, TemplateView):
    template_name = "report/active_projects.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ActiveProjectsView, self).get_context_data(
            *args, **kwargs)
        calc = ActiveProjectsCalculator()
        data = calc.calc(context.get('interval_start'),
                         context.get('interval_end'))
        context.update(data)
        return context


class ActiveProjectsExportView(LoggedInMixin, DaterangeMixin, View):
    def get(self, request, *args, **kwargs):
        self.get_params()

        calc = ActiveProjectsCalculator()
        data = calc.calc(self.interval_start, self.interval_end)

        # Find dates for displaying to the user
        start_str = self.interval_start.strftime('%Y%m%d')
        end_str = self.interval_end.strftime('%Y%m%d')
        filename = "active-projects-%s-%s" % (start_str, end_str)

        column_names = ['ID', 'Name', 'Project Number', 'Last worked on',
                        'Project Status', 'Caretaker', 'Hours logged']

        rows = [[x.pid, x.name, x.projnum, x.last_worked_on, x.status,
                 x.caretaker_user, interval_to_hours(x.hours_logged)]
                for x in data['projects']]

        generator = ReportFileGenerator()
        return generator.generate(
            column_names, rows, filename, self.request.GET.get('format'))


class YearlyReviewView(LoggedInMixin, View):
    def get(self, request):
        user = request.user.userprofile
        return HttpResponseRedirect("/report/user/%s/yearly/" % user.username)


class UserYearlyView(LoggedInMixin, TemplateView):
    template_name = "report/user_yearly.html"

    def get_context_data(self, **kwargs):
        context = super(UserYearlyView, self).get_context_data(**kwargs)
        username = kwargs['pk']
        user = get_object_or_404(UserProfile, username=username)
        now = timezone.now()
        interval_start = now + timedelta(days=-365)
        interval_end = now
        data = user.report(interval_start, interval_end)
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
        data = user.report(self.week_start, self.week_end)
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


class StaffReportView(LoggedInMixin, DaterangeMixin, TemplateView):
    template_name = "report/staff_report.html"

    def get_context_data(self, **kwargs):
        context = super(StaffReportView, self).get_context_data(**kwargs)

        calc = StaffReportCalculator(
            UserProfile.objects.filter(status='active', grp=False))

        data = calc.calc(self.interval_start, self.interval_end)

        context.update({
            'interval_start': self.interval_start,
            'interval_end': self.interval_end,
            'users': data
        })
        return context


class StaffReportExportView(LoggedInMixin, DaterangeMixin, View):
    def get(self, request, *args, **kwargs):
        self.get_params()
        calc = StaffReportCalculator(
            UserProfile.objects.filter(status='active', grp=False))
        data = calc.calc(self.interval_start, self.interval_end)

        start_str = self.interval_start.strftime('%Y%m%d')
        end_str = self.interval_end.strftime('%Y%m%d')
        filename = "staff-report-%s-%s" % (start_str, end_str)

        column_names = ['Staff Member', 'Hours Logged']

        rows = [
            [x['user'].fullname, interval_to_hours(x['user_time'])]
            for x in data]

        generator = ReportFileGenerator()
        return generator.generate(
            column_names, rows, filename, self.request.GET.get('format'))


class ResolvedView(LoggedInMixin, TemplateView):
    template_name = "report/resolved.html"

    def get_context_data(self, **kwargs):
        context = super(ResolvedView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.filter(status='RESOLVED')
        return context


class InprogressView(LoggedInMixin, TemplateView):
    template_name = "report/inprogress.html"

    def get_context_data(self, **kwargs):
        context = super(InprogressView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.filter(status='INPROGRESS')
        return context


class PassedMilestonesView(LoggedInMixin, TemplateView):
    template_name = "report/passed_milestones.html"

    def get_context_data(self, **kwargs):
        context = super(PassedMilestonesView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.filter(status='RESOLVED')

        now = timezone.now()
        context['milestones'] = Milestone.objects.filter(
            status='OPEN',
            target_date__lt=now,
            ).order_by("target_date").select_related('project')

        return context


class TimeSpentByUser(LoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        calc = TimeSpentByUserCalculator()
        data = calc.calc()

        now = timezone.now()
        filename = 'time-spent-by-user-{}'.format(now.strftime('%Y-%m-%d'))

        column_names = [
            'Project Name', 'Milestone Name', 'Task Name', 'Task Status',
            'Assigned to', 'Project Status', 'Estimated Time',
            'Time Spent', 'Task Due Date', 'Task Modified Date',
            'Project Due Date',
            'Caretaker', 'Task Description', 'Comment History'
        ]

        generator = ReportFileGenerator()
        return generator.generate(column_names, data, filename, 'csv')


class TimeSpentByProject(LoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        calc = TimeSpentByProjectCalculator()
        data = calc.calc()

        now = timezone.now()
        filename = 'time-spent-by-project-{}'.format(now.strftime('%Y-%m-%d'))

        column_names = ['Project Name', 'Status', 'Estimated Time',
                        'Time Spent', 'Due Date', 'Caretaker']

        generator = ReportFileGenerator()
        return generator.generate(column_names, data, filename, 'csv')


class ProjectStatus(LoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        calc = ProjectStatusCalculator()
        data = calc.calc()

        now = timezone.now()
        filename = 'project-status-{}'.format(now.strftime('%Y-%m-%d'))

        column_names = [
            'Category',
            'Project Name',
            'Project Status',
            'Caretaker',
            'Project Due Date',
            '% of Tasks Open',
            '% of Tasks In-Progress',
            '% of Tasks Complete',
            'Original Estimate',
            'Time Spent',
        ]

        generator = ReportFileGenerator()
        return generator.generate(column_names, data, filename, 'csv')


class StaffCapacityView(LoggedInMixin, DaterangeMixin, TemplateView):
    template_name = "report/staff_capacity.html"

    def get_default_start(self):
        return self.today()

    def get_default_end(self):
        return self.today() + relativedelta(days=6)

    def get_context_data(self, **kwargs):
        context = super(StaffCapacityView, self).get_context_data(**kwargs)

        calc = StaffCapacityCalculator(
            UserProfile.objects.filter(status='active', grp=False),
            self.interval_start, self.interval_end)

        data = calc.calc()

        context.update({
            'days': calc.days,
            'interval_start': self.interval_start,
            'interval_end': self.interval_end,
            'users': data
        })
        return context


class StaffCapacityExportView(LoggedInMixin, DaterangeMixin, View):

    def user_group(self, user_profile):
        if user_profile.primary_group:
            return user_profile.primary_group.group_fullname().capitalize()
        return ''

    def get(self, request, *args, **kwargs):
        self.get_params()
        calc = StaffCapacityCalculator(
            UserProfile.objects.filter(status='active', grp=False),
            self.interval_start, self.interval_end)
        data = calc.calc()

        start_str = self.interval_start.strftime('%Y%m%d')
        end_str = self.interval_end.strftime('%Y%m%d')
        filename = "staff-capacity-%s-%s" % (start_str, end_str)

        column_names = ['Staff Member', 'Group', 'Capacity', 'Booked',
                        '% Booked', 'Available', '% Available']

        rows = [
            [x['user'].fullname,
             self.user_group(x['user']),
             x['capacity'],
             x['booked'],
             x['percent_booked'],
             x['available'],
             x['percent_available']]
            for x in data]

        generator = ReportFileGenerator()
        return generator.generate(
            column_names, rows, filename, self.request.GET.get('format'))

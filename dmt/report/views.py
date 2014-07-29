from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View
import StringIO
from dmt.claim.models import Claim
from dmt.main.models import User, Item, Milestone
from dmt.main.views import LoggedInMixin
from dmt.main.utils import interval_to_hours
from .models import (
    ActiveProjectsCalculator, StaffReportCalculator,
    WeeklySummaryReportCalculator)
from .mixins import PrevNextWeekMixin


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
        return context


class ActiveProjectsExportView(LoggedInMixin, View):
    def export_csv(self, data, columns, filename):
        """
        Generates the report as a CSV. Returns an HttpResponse.
        """
        import unicodecsv

        filename += '.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            "attachment; filename=\"%s\"" % (filename)

        writer = unicodecsv.writer(response)
        writer.writerow(columns)
        for p in data['projects']:
            writer.writerow([p.pid, p.name, p.projnum, p.last_worked_on,
                             p.status, p.caretaker,
                             interval_to_hours(p.hours_logged)])
        return response

    def export_excel(self, data, columns, filename):
        """
        Generates the report as an MS Excel file. Returns an HttpResponse.
        """
        import xlsxwriter

        # Excel
        filename += '.xlsx'
        output = StringIO.StringIO()
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-' +
            'officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = \
            "attachment; filename=\"%s\"" % (filename)

        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        for i in range(len(columns)):
            worksheet.write(0, i, columns[i], bold)

        row = 1
        for p in data['projects']:
            # Some of these table cells have problems when being written
            # with write_row(), so we stub them out and write to those
            # cells with an explicit type.
            worksheet.write_row(row, 0,
                                [p.pid, p.name, p.projnum, None, p.status,
                                 None, interval_to_hours(p.hours_logged)])
            worksheet.write_string(row, 3, str(p.last_worked_on))
            worksheet.write_string(row, 5, str(p.caretaker))
            row += 1

        workbook.close()

        output.seek(0)
        response.write(output.read())

        return response

    def get(self, request, **kwargs):
        now = datetime.now()
        filename = "active-projects-%s-%s-%s" % (now.year, now.month, now.day)
        columns = ['ID', 'Name', 'Project Number', 'Last worked on',
                   'Project Status', 'Caretaker', 'Hours logged']

        days = 31
        if kwargs['days']:
            days = int(kwargs['days'])
        calc = ActiveProjectsCalculator()
        data = calc.calc(days)

        if kwargs['format'] == 'csv':
            return self.export_csv(data, columns, filename)
        else:
            return self.export_excel(data, columns, filename)


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
        report = StaffReportCalculator(['programmers', 'video', 'designers',
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

        report = WeeklySummaryReportCalculator(['programmers', 'designers',
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

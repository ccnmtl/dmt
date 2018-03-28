from datetime import date

from django.db import connection
from django.db.models import Q, Sum
import numpy

from dmt.main.models import Project, Item


class ActiveProjectsCalculator(object):
    def calc(self, interval_start, interval_end):
        projects = Project.projects_active_between(
            interval_start, interval_end)
        total_hours = round(
            sum([p.hours_logged.total_seconds() for p in projects]) / 3600, 2)
        return dict(projects=projects,
                    total_hours=total_hours)


class StaffReportCalculator(object):
    def __init__(self, users):
        self.users = users
        self.user_reports = []

    def calc(self, start, end):
        user_data = []
        for user in self.users:
            user_data.append({
                'user': user,
                'resolved_items': user.resolved_items_for_interval(
                    start, end).count(),
                'user_time': user.interval_time(start, end),
            })
        return user_data


class TimeSpentByUserCalculator(object):
    def calc(self):
        report = []
        with connection.cursor() as cursor:
            cursor.execute('''
select
        projects.name as project_name,
        items.title as task_title,
        items.status as task_status,
        users.fullname as assigned_to,
        projects.status as project_status,
        extract(epoch from items.estimated_time) / 3600 as estimated_time,
        sum(extract(epoch from actual_times.actual_time)) / 3600 as time_spent,
        items.target_date as task_due_date,
        projects.due_date as project_due_date,
        caretakers.fullname as caretaker
from projects
join milestones on (projects.pid = milestones.pid)
join items on (milestones.mid = items.mid)
left join actual_times on (items.iid = actual_times.iid)
left join users as "caretakers" on
            (caretakers.user_id = projects.caretaker_user_id)
join users on (items.assigned_user = users.user_id)
where projects.status != 'Defunct' and projects.status != 'Non-project'
    and projects.pub_view
and milestones.name != 'Someday/Maybe'
group by items.iid, users.fullname, projects.pid, milestones.name,
    caretakers.fullname
order by assigned_to, task_due_date, project_name
limit 100000;
            ''')
            report = cursor.fetchall()

        return report


class TimeSpentByProjectCalculator(object):
    def calc(self):
        report = []
        with connection.cursor() as cursor:
            cursor.execute('''
select
        projects.name, projects.status,
        sum(extract(epoch from items.estimated_time)) / 3600 as estimated_time,
        sum(extract(epoch from actual_times.actual_time)) / 3600 as time_spent,
        projects.due_date as due_date,
        caretakers.fullname as caretaker
from projects
join milestones on (projects.pid = milestones.pid)
join items on (milestones.mid = items.mid)
left join actual_times on (items.iid = actual_times.iid)
left join users as "caretakers" on
            (caretakers.user_id = projects.caretaker_user_id)
where projects.status != 'Defunct' and projects.status != 'Non-project'
    and projects.pub_view
group by projects.pid, caretakers.fullname
order by due_date, projects.name
limit 100000;
            ''')
            report = cursor.fetchall()

        return report


def percentage_of(a, b):
    return 100 * round(a / b, 2) if b else None


class ProjectStatusCalculator(object):
    def calc(self):
        report = []

        projects = Project.objects.filter(
            ~Q(status='Defunct') & ~Q(status='Non-project')
            & Q(pub_view=True)
        ).annotate(
            estimate=Sum('milestone__item__estimated_time')
        ).annotate(
            time_spent=Sum('milestone__item__actualtime__actual_time')
        ).order_by('category', 'name')

        for project in projects:
            milestones = project.milestones()
            milestone = milestones.order_by('-target_date').first()
            all_tasks = Item.objects.filter(milestone__in=milestones)
            all_tasks_count = float(all_tasks.count())
            open_tasks = all_tasks.filter(status='OPEN')
            inprogress_tasks = all_tasks.filter(status='INPROGRESS')
            completed_tasks = all_tasks.filter(
                Q(status='RESOLVED') | Q(status='VERIFIED'))

            estimate = 0
            if project.estimate:
                estimate = round(
                    project.estimate.total_seconds() / 3600.0, 2)

            time_spent = 0
            if project.time_spent:
                time_spent = round(
                    project.time_spent.total_seconds() / 3600.0, 2)

            report.append([
                project.category,
                project.name,
                project.status,
                project.caretaker_user.userprofile.fullname,
                milestone.target_date if milestone else None,
                percentage_of(open_tasks.count(), all_tasks_count),
                percentage_of(inprogress_tasks.count(), all_tasks_count),
                percentage_of(completed_tasks.count(), all_tasks_count),
                estimate,
                time_spent,
            ])

        return sorted(report, key=lambda row: row[3] or date(2000, 1, 1))


class StaffCapacityCalculator(object):

    def __init__(self, users, start, end):
        self.users = users
        self.interval_start = start
        self.interval_end = end

    def holidays(self):
        # http://hr.columbia.edu/events/holidays
        dates = ['2018-01-01', '2018-01-02', '2018-01-15', '2018-02-19',
                 '2018-05-28', '2018-07-04', '2018-09-03', '2018-11-06',
                 '2018-11-22', '2018-11-23', '2018-12-24', '2018-12-25',
                 '2018-12-31', '2019-01-01']
        return [numpy.datetime64(x) for x in dates]

    def days(self):
        return numpy.busday_count(self.interval_start, self.interval_end,
                                  holidays=self.holidays())

    def capacity_for_range(self):
        return self.days() * 6  # in hours

    def calc(self):
        capacity = self.capacity_for_range()
        user_data = []
        for user in self.users:
            booked = user.assigned_time_for_interval(
                self.interval_start, self.interval_end)
            avail = capacity - booked

            user_data.append({
                'user': user,
                'capacity': capacity,
                'booked': booked,
                'percent_booked': format(booked / capacity * 100, '.1f'),
                'available': avail,
                'percent_available': format(avail / capacity * 100, '.1f'),
            })
        return user_data

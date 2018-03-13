from django.db import connection
from dmt.main.models import Project


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
        users.fullname as assigned_to,
        projects.status as project_status,
        extract(epoch from items.estimated_time) / 3600 as estimated_time,
        sum(extract(epoch from actual_times.actual_time)) / 3600 as time_spent,
        items.target_date as task_due_date,
        max(milestones.target_date) as project_due_date
from projects
join milestones on (projects.pid = milestones.pid)
join items on (milestones.mid = items.mid)
join actual_times on (items.iid = actual_times.iid)
join users on (items.assigned_user = users.user_id)
where projects.status != 'Defunct' and projects.status != 'Non-project'
and milestones.name != 'Someday/Maybe'
group by items.iid, users.fullname, projects.pid, milestones.name
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
        max(milestones.target_date) as due_date
from projects
join milestones on (projects.pid = milestones.pid)
join items on (milestones.mid = items.mid)
join actual_times on (items.iid = actual_times.iid)
where projects.status != 'Defunct' and projects.status != 'Non-project'
and actual_times.completed >= '2017-01-23'
group by projects.pid
order by due_date, projects.name
limit 100000;
            ''')
            report = cursor.fetchall()

        return report

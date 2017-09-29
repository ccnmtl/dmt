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

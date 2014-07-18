from datetime import datetime, timedelta
from dmt.main.models import ActualTime, InGroup, Project, User


class ActiveProjectsCalculator(object):
    def calc(self, days):
        now = datetime.now()
        end = now
        start = now - timedelta(days=days)
        projects = Project.projects_active_between(start, end)
        total_hours = round(
            sum([p.hours_logged.total_seconds() for p in projects]) / 3600, 2)
        return dict(days=days,
                    projects=projects,
                    total_hours=total_hours)


class StaffReportCalculator(object):
    def __init__(self, groups):
        self.groups = groups
        self.user_reports = []

    def calc(self, start, end):
        user_data = []
        for grp in self.groups:
            try:
                group_user = User.objects.get(username="grp_" + grp)
            except User.DoesNotExist:
                continue

            for user in group_user.users_in_group():
                existing_user = \
                    [x for x in user_data
                     if x['user'].username == user.username]
                if existing_user:
                    # This user is already in our user_data list. This means
                    # they belong to more than one group that we're reporting
                    # on. In this case, it's safe to just skip this duplicate
                    # entry.
                    continue

                user_time = user.interval_time(start, end)
                group_name = InGroup.verbose_name(group_user.fullname)
                user_data.append(dict(user=user, user_time=user_time,
                                      group_name=group_name))

        return dict(users=user_data)


class WeeklySummaryReportCalculator(object):
    def __init__(self, groups):
        groupnames = ['grp_' + x for x in groups]
        self.groups = User.objects.filter(username__in=groupnames)
        self.groupnames = [InGroup.verbose_name(x.fullname)
                           for x in self.groups]

    def calc(self, start, end):
        projects = Project.projects_active_during(start, end, self.groups)
        my_projects = []
        for p in projects:
            d = dict(
                pid=p.pid,
                name=p.name,
                projnum=p.projnum)
            d['group_times'] = [p.group_hours(g.username, start, end)
                                for g in self.groups]
            d['total_time'] = p.interval_total(start, end)
            my_projects.append(d)

        group_totals = [x.total_group_time(start, end) for x in self.groups]
        grand_total = ActualTime.interval_total_time(start, end)

        return dict(groupnames=self.groupnames,
                    project_times=my_projects,
                    group_totals=group_totals,
                    grand_total=grand_total)

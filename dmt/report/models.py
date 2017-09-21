from dmt.main.models import InGroup, Project, UserProfile


class ActiveProjectsCalculator(object):
    def calc(self, interval_start, interval_end):
        projects = Project.projects_active_between(
            interval_start, interval_end)
        total_hours = round(
            sum([p.hours_logged.total_seconds() for p in projects]) / 3600, 2)
        return dict(projects=projects,
                    total_hours=total_hours)


class StaffReportCalculator(object):
    def __init__(self, groups):
        self.groups = groups
        self.user_reports = []

    def calc(self, start, end):
        user_data = []
        for grp in self.groups:
            try:
                group_user = UserProfile.objects.get(username="grp_" + grp)
            except UserProfile.DoesNotExist:
                # If we can't find a group under this name, just
                # continue to the next iteration of the loop.
                continue

            # Find all users whose primary group is the selected group.
            users = UserProfile.objects.filter(primary_group=group_user,
                                               status='active')

            for user in users:
                user_time = user.interval_time(start, end)
                group_name = InGroup.verbose_name(group_user.fullname)
                group_username = group_user.username
                user_data.append(dict(user=user, user_time=user_time,
                                      group_name=group_name,
                                      group_username=group_username))

        return dict(users=user_data)

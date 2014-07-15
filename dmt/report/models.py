from dmt.main.models import InGroup, User


class StaffReportCalculator(object):
    def __init__(self, groups):
        self.groups = groups
        self.group_reports = []

    def calc(self, start, end):
        for grp in self.groups:
            try:
                group_user = User.objects.get(username="grp_" + grp)
            except User.DoesNotExist:
                continue
            group_total_time = group_user.total_group_time(start, end)
            data = dict(group=InGroup.verbose_name(group_user.fullname),
                        total_time=group_total_time)
            user_data = []
            for user in group_user.users_in_group():
                user_time = user.interval_time(start, end)
                user_data.append(dict(user=user, user_time=user_time))
            data['user_data'] = user_data
            data['max_time'] = max(u['user_time'] for u in user_data)
            self.group_reports.append(data)

        group_times = [g['total_time'] for g in self.group_reports]
        group_max_time = max(group_times) if group_times else 0
        return dict(groups=self.group_reports, group_max_time=group_max_time)

from datetime import datetime, timedelta


class PrevNextWeekMixin(object):
    def __init__(self):
        now = datetime.today()
        self.calc_weeks(now)

    def calc_weeks(self, now):
        self.week_start = now + timedelta(days=-now.weekday())
        self.week_end = self.week_start + timedelta(days=6)
        self.prev_week = self.week_start - timedelta(weeks=1)
        self.next_week = self.week_start + timedelta(weeks=1)

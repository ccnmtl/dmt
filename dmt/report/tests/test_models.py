from datetime import datetime, timedelta
from django.test import TestCase
from ..models import StaffReportCalculator


class StaffReportCalculatorTests(TestCase):
    def setUp(self):
        now = datetime.today()
        self.week_start = now + timedelta(days=-now.weekday())
        self.week_end = self.week_start + timedelta(days=6)

    def test_calc_no_groups(self):
        calc = StaffReportCalculator([])
        calc.calc(self.week_start, self.week_end)

    def test_calc_on_empty_db(self):
        calc = StaffReportCalculator(['programmers'])
        calc.calc(self.week_start, self.week_end)

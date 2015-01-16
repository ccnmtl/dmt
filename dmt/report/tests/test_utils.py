from django.test import TestCase
from dmt.report.utils import ReportFileGenerator


class ReportFileGeneratorTests(TestCase):
    def setUp(self):
        self.generator = ReportFileGenerator()
        self.test_column_names = ['ID', 'username']
        self.test_rows = [[2, 'abc'], [4, 'test_user']]

    def test_generate_empty_csv(self):
        self.generator.generate([], [], 'test', 'csv')

    def test_generate_csv(self):
        self.generator.generate(
            self.test_column_names,
            self.test_rows,
            'test',
            'csv')

    def test_generate_empty_excel(self):
        self.generator.generate([], [], 'test', 'xlsx')

    def test_generate_excel(self):
        self.generator.generate(
            self.test_column_names,
            self.test_rows,
            'test',
            'excel')

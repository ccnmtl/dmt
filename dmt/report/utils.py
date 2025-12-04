from __future__ import unicode_literals

from django.http import HttpResponse
from django.utils.encoding import smart_str


class ReportFileGenerator(object):
    """
    Class for generating report files in various formats.
    """

    def _gen_csv(self):
        """
        Generates the report as a CSV. Returns an HttpResponse.
        """
        import unicodecsv

        filename = self.filename + '.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            "attachment; filename=\"%s\"" % (filename)

        writer = unicodecsv.writer(response)
        writer.writerow(self.column_names)

        for row in self.rows:
            writer.writerow(row)

        return response

    def _gen_excel(self):
        """
        Generates the report as an MS Excel file. Returns an HttpResponse.
        """
        from io import BytesIO
        import xlsxwriter

        # Excel
        filename = self.filename + '.xlsx'
        output = BytesIO()
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-' +
            'officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = \
            "attachment; filename=\"%s\"" % (filename)

        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})

        for i in range(len(self.column_names)):
            worksheet.write(0, i, self.column_names[i], bold)

        i = 1
        for row in self.rows:
            rowdata = [smart_str(x) for x in row]
            worksheet.write_row(i, 0, rowdata)
            i += 1

        workbook.close()

        output.seek(0)
        response.write(output.read())

        return response

    def generate(self, column_names, rows, filename, fmt):
        """Make a report.

        Arguments:
        column_names -- Column names to use for the table header.
        rows -- Rows of data.
        filename -- The filename to use, without the extension.
        fmt -- The format of the report (e.g. 'csv', 'xlsx').
        """
        self.column_names = column_names
        self.rows = rows
        self.filename = filename
        self.fmt = fmt

        if (self.fmt == 'csv'):
            return self._gen_csv()
        else:
            return self._gen_excel()

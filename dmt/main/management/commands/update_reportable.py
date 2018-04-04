import csv

from django.core.management.base import BaseCommand

from dmt.main.models import Project


class Command(BaseCommand):

    def process_file(self, row):
        p = Project.objects.get(pid=row[0])
        p.pub_view = row[3] == 't'
        p.save()

    def add_arguments(self, parser):
        # where the inventory directories live
        parser.add_argument('path', type=str)

    def handle(self, *args, **kwargs):
        local_path = kwargs['path']
        f = open(local_path, 'r')
        reader = csv.reader(f)
        for row in reader:
            self.process_file(row)

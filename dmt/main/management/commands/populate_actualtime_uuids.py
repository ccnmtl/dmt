import uuid
from django.core.management.base import BaseCommand
from dmt.main.models import ActualTime


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Assign uuids to ActualTimes that don't have one."""
        for time in ActualTime.objects.all():
            time.uuid = uuid.uuid4()
            time.save()

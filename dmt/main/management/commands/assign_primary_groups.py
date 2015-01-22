from django.core.management.base import BaseCommand
from dmt.main.models import UserProfile, InGroup


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Give each user a primary group.

        This command picks the first InGroup object associated with each
        user and uses that as the primary group.

        We will need to fine-tune the primary groups after running this
        command, but this provides an alright default.
        """

        for up in UserProfile.objects.filter(status='active'):
            groups = InGroup.objects.filter(username=up)
            group = groups.first()
            if (group is not None) and (up.primary_group is None):
                grp = group.grp
                up.primary_group = grp
                up.save()

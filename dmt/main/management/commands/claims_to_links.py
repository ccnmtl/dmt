from django.core.management.base import BaseCommand
from dmt.claim.models import Claim


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """convert each Claim entry to a direct
        OneToOne link"""

        for c in Claim.objects.all():
            user = c.django_user
            profile = c.pmt_user
            if profile.user is None:
                user.userprofile = profile
                user.save()

"""

For every PMT UserProfile, we make sure there
is a (de-activated) Django user account and Claim
to match.

All active PMT users should already have claimed their
accounts, so this should only be filling in old accounts
for the sake of working towards eliminating the
Claim mechanism.

See: https://pmt.ccnmtl.columbia.edu/forum/4532/

This command can be deleted once it's been run on production
since all new accounts get everything set up properly.
"""

from django.core.management.base import BaseCommand
from dmt.main.models import UserProfile
from dmt.claim.models import Claim
from django.contrib.auth.models import User


def user_already_exists(username):
    return User.objects.filter(username=username).exists()


def first_last(fullname):
    """ try to pull a first/last name out of a fullname

    Don't do anything complicated. Just split on space
    if possible. This is all for creating inactive
    Users, so don't worry about it too much.
    """
    if " " in fullname:
        return fullname.split(" ", 1)
    return (fullname, fullname)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        claimed = set([c.pmt_user.username for c in Claim.objects.all()])
        for up in UserProfile.objects.all():
            if up.username in claimed:
                continue
            if user_already_exists(up.username):
                print (
                    "a django user with username '%s' already exists"
                    "this will need to be handled manually" % up.username)
                continue
            (first, last) = first_last(up.fullname)
            u = User.objects.create(
                username=up.username,
                first_name=first,
                last_name=last,
                email=up.email,
                is_staff=False,
                is_active=False,
                is_superuser=False,
            )
            u.set_unusable_password()
            u.save()

            c = Claim.objects.create(
                pmt_user=up,
                django_user=u,
            )

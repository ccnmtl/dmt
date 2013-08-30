from django.db import models
from django.contrib.auth.models import User as DjangoUser
from dmt.main.models import User as PMTUser


class Claim(models.Model):
    django_user = models.ForeignKey(DjangoUser, unique=True)
    pmt_user = models.ForeignKey(PMTUser, unique=True)

    def __unicode__(self):
        return "%s has claimed %s" % (
            self.django_user.username,
            self.pmt_user.username)


def all_unclaimed_pmt_users():
    """ active PMT Users who are not yet claimed by a Django User
    """
    return PMTUser.objects.filter(
        status='active'
    ).exclude(
        username__startswith="grp_").exclude(
        username__in=[c.pmt_user.username for c in Claim.objects.all()]
    )

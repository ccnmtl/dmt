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

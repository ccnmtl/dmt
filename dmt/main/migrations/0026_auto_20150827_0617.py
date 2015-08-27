# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20150827_0616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actualtime',
            name='user',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]

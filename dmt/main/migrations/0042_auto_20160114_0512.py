# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_auto_20160113_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusupdate',
            name='author',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]

# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_auto_20160127_0901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='assigned_user',
            field=models.ForeignKey(related_name='assigned_to', db_column=b'assigned_user', default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='item',
            name='owner_user',
            field=models.ForeignKey(related_name='owned_items', db_column=b'owner_user', default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]

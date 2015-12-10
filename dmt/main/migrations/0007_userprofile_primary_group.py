# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_remove_userprofile_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='primary_group',
            field=models.ForeignKey(blank=True, to='main.UserProfile', null=True),
            preserve_default=True,
        ),
    ]

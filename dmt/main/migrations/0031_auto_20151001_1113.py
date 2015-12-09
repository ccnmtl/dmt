# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_remove_notifyproject_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notifyproject',
            name='pid',
        ),
        migrations.RemoveField(
            model_name='notifyproject',
            name='user',
        ),
        migrations.DeleteModel(
            name='NotifyProject',
        ),
    ]

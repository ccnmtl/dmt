# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_remove_workson_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actualtime',
            name='resolver',
        ),
    ]

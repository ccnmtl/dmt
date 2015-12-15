# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_auto_20151214_0830'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workson',
            name='username',
        ),
    ]

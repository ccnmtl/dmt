# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_auto_20160114_0512'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statusupdate',
            name='user',
        ),
    ]

# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_auto_20150904_0729'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='author',
        ),
    ]

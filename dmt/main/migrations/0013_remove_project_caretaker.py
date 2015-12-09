# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20150309_0838'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='caretaker',
        ),
    ]

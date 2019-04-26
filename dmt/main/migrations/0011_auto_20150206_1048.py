# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20150126_0732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='status',
            field=models.CharField(db_index=True, max_length=16, choices=[('OPEN', 'OPEN'), ('INPROGRESS', 'IN PROGRESS'), ('RESOLVED', 'RESOLVED'), ('VERIFIED', 'VERIFIED')]),
            preserve_default=True,
        ),
    ]

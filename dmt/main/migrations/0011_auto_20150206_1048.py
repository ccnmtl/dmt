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
            field=models.CharField(db_index=True, max_length=16, choices=[(b'OPEN', b'OPEN'), (b'INPROGRESS', b'IN PROGRESS'), (b'RESOLVED', b'RESOLVED'), (b'VERIFIED', b'VERIFIED')]),
            preserve_default=True,
        ),
    ]

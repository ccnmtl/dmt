# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20150513_0507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(default=b'New', max_length=16, blank=True, choices=[(b'New', b'New'), (b'Development', b'Development'), (b'Deployment', b'Deployment'), (b'Defunct', b'Defunct'), (b'Deferred', b'Deferred'), (b'Non-project', b'Non-project')]),
        ),
    ]

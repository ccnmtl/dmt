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
            field=models.CharField(default='New', max_length=16, blank=True, choices=[('New', 'New'), ('Development', 'Development'), ('Deployment', 'Deployment'), ('Defunct', 'Defunct'), ('Deferred', 'Deferred'), ('Non-project', 'Non-project')]),
        ),
    ]

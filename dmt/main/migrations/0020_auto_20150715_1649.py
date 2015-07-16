# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20150605_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actualtime',
            name='actual_time',
            field=models.DurationField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='estimated_time',
            field=models.DurationField(null=True, blank=True),
        ),
    ]

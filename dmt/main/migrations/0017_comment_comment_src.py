# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_timestamptz'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment_src',
            field=models.TextField(blank=True),
        ),
    ]

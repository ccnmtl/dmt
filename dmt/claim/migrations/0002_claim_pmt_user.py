# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
        ('claim', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='pmt_user',
            field=models.ForeignKey(to='main.User', unique=True),
            preserve_default=True,
        ),
    ]

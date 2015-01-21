# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('claim', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='claim',
            name='django_user',
        ),
        migrations.RemoveField(
            model_name='claim',
            name='pmt_user',
        ),
        migrations.DeleteModel(
            name='Claim',
        ),
    ]

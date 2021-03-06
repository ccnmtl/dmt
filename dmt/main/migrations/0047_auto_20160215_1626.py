# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-15 21:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0046_auto_20160127_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='pub_view',
            field=models.BooleanField(
                default=False,
                help_text='This checkbox determines whether ' +
                'this project is visible in reports.',
                verbose_name='Public'),
        ),
    ]

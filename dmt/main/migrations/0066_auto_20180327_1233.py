# flake8: noqa
# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-27 16:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0065_auto_20180323_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='category',
            field=models.CharField(blank=True, choices=[('Admin', 'Admin'), ('Curriculum RFP', 'Curriculum RFP'), ('Funded', 'Funded'), ('Hybrid RFP', 'Hybrid RFP'), ('MOOC', 'MOOC'), ('Small RFP', 'Small RFP'), ('Strategic', 'Strategic'), ('Support', 'Support')], max_length=32, null=True, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='project',
            name='due_date',
            field=models.DateField(blank=True, help_text='This is the date that the project is completed and deployed.', null=True, verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='project',
            name='launch_date',
            field=models.DateField(blank=True, help_text='This is the date the project launches, eg. a MOOC launch.', null=True, verbose_name='Launch Date'),
        ),
        migrations.AlterField(
            model_name='project',
            name='start_date',
            field=models.DateField(blank=True, help_text='This is the date that work starts.', null=True, verbose_name='Start Date'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-05 16:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0061_project_internal'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='technology',
            field=models.CharField(
                blank=True,
                choices=[('Django', 'Django'),
                         ('Hugo', 'Hugo'),
                         ('Drupal 5', 'Drupal 5'),
                         ('Drupal 7', 'Drupal 7')],
                max_length=255, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-12 18:28
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0067_auto_20180328_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_manager_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_manager', to=settings.AUTH_USER_MODEL),
        ),
    ]

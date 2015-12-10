# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0032_auto_20151029_1155'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reminder_time', models.DurationField(help_text=b'Enter time and unit. For example: <code>1d</code> to be reminded one day before the target date.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('item', models.ForeignKey(to='main.Item')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='reminder',
            unique_together=set([('user', 'item')]),
        ),
    ]

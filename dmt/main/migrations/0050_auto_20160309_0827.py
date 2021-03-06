# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-09 13:27
from __future__ import unicode_literals

from django.db import migrations
import uuid


def gen_uuid(apps, schema_editor):
    ActualTime = apps.get_model('main', 'ActualTime')
    for row in ActualTime.objects.filter(uuid=None):
        row.uuid = uuid.uuid4()
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0049_actualtime_uuid'),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]

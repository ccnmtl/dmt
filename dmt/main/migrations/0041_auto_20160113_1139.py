# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


def backfill_statusupdate_author(apps, schema_editor):
    StatusUpdate = apps.get_model('main', 'StatusUpdate')
    for statusupdate in StatusUpdate.objects.all():
        statusupdate.author = statusupdate.user.user
        statusupdate.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_remove_attachment_author'),
    ]

    operations = [
        migrations.RunPython(backfill_statusupdate_author)
    ]

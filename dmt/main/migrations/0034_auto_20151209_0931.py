# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


def backfill_attachment_users(apps, schema_editor):
    Attachment = apps.get_model("main", "Attachment")
    for attachment in Attachment.objects.filter(user=None):
        attachment.user = attachment.author.user
        attachment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_auto_20151120_1112'),
    ]

    operations = [
        migrations.RunPython(backfill_attachment_users),
    ]

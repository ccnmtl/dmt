# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def backfill_users(apps, schema_editor):
    Node = apps.get_model('main', 'Node')

    for node in Node.objects.all():
        if node.user is not None:
            # don't need to backfill it
            continue
        node.user = node.author.userprofile
        node.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20150206_1048'),
    ]

    operations = [
    ]

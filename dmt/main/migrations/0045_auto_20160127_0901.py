# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def populate_owner_assigned(apps, schema_editor):
    Item = apps.get_model("main", "Item")
    for item in Item.objects.all():
        if item.assigned_user is None:
            item.assigned_user = item.assigned_to.user
        if item.owner_user is None:
            item.owner_user = item.owner.user
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_auto_20160120_1454'),
    ]

    operations = [
        migrations.RunPython(populate_owner_assigned),
    ]

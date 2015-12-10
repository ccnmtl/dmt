# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def merge_urls(apps, schema_editor):
    Item = apps.get_model("main", "Item")
    for item in Item.objects.all():
        if item.url != None and item.url != "":
            item.description = item.description + "\n\n" + item.url
            item.url = None
            item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20150122_0711'),
    ]

    operations = [
        migrations.RunPython(merge_urls),
    ]

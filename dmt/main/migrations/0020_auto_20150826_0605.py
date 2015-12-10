# flake8: noqa
# -*- coding: utf-8 -*-
from django.db import models, migrations


def document_author_to_user(apps, schema_editor):
    Document = apps.get_model("main", "Document")
    for document in Document.objects.all():
        document.user = document.author.user
        document.save()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0019_auto_20150605_1607'),
    ]

    operations = [
        migrations.RunPython(document_author_to_user)
    ]

# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def project_status_terminology_change(apps, schema_editor):
    changes = [
        ("Discovery", "New"),
        ("Design", "Development"),
        ("Maintenance", "Deployment"),
        ("Complete", "Deployment"),
        ("planning", "Non-project"),
    ]
    Project = apps.get_model("main", "Project")
    for old, new in changes:
        for project in Project.objects.filter(status=old):
            project.status = new
            project.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_remove_project_caretaker'),
    ]

    operations = [
        migrations.RunPython(project_status_terminology_change),
    ]

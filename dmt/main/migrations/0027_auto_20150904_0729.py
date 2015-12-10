# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def notify_project_username_to_user(apps, schema_editor):
    NotifyProject = apps.get_model("main", "NotifyProject")
    for np in NotifyProject.objects.all():
        np.user = np.username.user


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_auto_20150827_0617'),
    ]

    operations = [
        migrations.RunPython(notify_project_username_to_user)
    ]

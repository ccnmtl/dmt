# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_remove_node_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notifyproject',
            name='username',
        ),
    ]

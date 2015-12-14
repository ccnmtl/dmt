# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_remove_client_contact'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='notify',
            unique_together=set([('item', 'user')]),
        ),
        migrations.RemoveField(
            model_name='notify',
            name='username',
        ),
    ]

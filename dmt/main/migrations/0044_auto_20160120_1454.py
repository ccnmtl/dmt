# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_remove_statusupdate_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milestone',
            name='name',
            field=models.TextField(),
        ),
    ]

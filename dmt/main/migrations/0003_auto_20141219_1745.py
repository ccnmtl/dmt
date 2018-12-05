# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20141219_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingroup',
            name='grp',
            field=models.ForeignKey(related_name='group_members', db_column='grp', to='main.UserProfile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='assigned_to',
            field=models.ForeignKey(related_name='assigned_items', db_column='assigned_to', to='main.UserProfile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='owner',
            field=models.ForeignKey(related_name='owned_items', db_column='owner', to='main.UserProfile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notify',
            name='item',
            field=models.ForeignKey(related_name='notifies', db_column='iid', to='main.Item'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='area',
            field=models.CharField(max_length=100, verbose_name='Discipline', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='distrib',
            field=models.CharField(max_length=20, verbose_name='Distribution', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='entry_rel',
            field=models.BooleanField(default=False, verbose_name='Released'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='eval_url',
            field=models.CharField(max_length=255, verbose_name='Evaluation URL', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='info_url',
            field=models.CharField(max_length=255, verbose_name='Information URL', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Project name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='poster',
            field=models.BooleanField(default=False, verbose_name='Poster project'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='projnum',
            field=models.IntegerField(null=True, verbose_name='Project number', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='pub_view',
            field=models.BooleanField(default=False, verbose_name='PMT View'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='url',
            field=models.CharField(max_length=255, verbose_name='Project URL', blank=True),
            preserve_default=True,
        ),
    ]

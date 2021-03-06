# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActualTime',
            fields=[
                ('actual_time', models.DurationField(null=True, blank=True)),
                ('completed', models.DateTimeField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'actual_times',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filename', models.CharField(max_length=128, blank=True)),
                ('title', models.CharField(max_length=128, blank=True)),
                ('type', models.CharField(max_length=8, blank=True)),
                ('url', models.CharField(max_length=256, blank=True)),
                ('description', models.TextField(blank=True)),
                ('last_mod', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'attachment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('client_id', models.AutoField(serialize=False, primary_key=True)),
                ('lastname', models.CharField(max_length=64, blank=True)),
                ('firstname', models.CharField(max_length=64, blank=True)),
                ('title', models.CharField(max_length=128, blank=True)),
                ('registration_date', models.DateField(null=True, blank=True)),
                ('department', models.CharField(max_length=255, blank=True)),
                ('school', models.CharField(max_length=255, blank=True)),
                ('add_affiliation', models.CharField(max_length=255, blank=True)),
                ('phone', models.CharField(max_length=32, blank=True)),
                ('email', models.CharField(max_length=128, blank=True)),
                ('comments', models.TextField(blank=True)),
                ('status', models.CharField(max_length=16, blank=True)),
                ('email_secondary', models.CharField(max_length=128, blank=True)),
                ('phone_mobile', models.CharField(max_length=32, blank=True)),
                ('phone_other', models.CharField(max_length=32, blank=True)),
                ('website_url', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'ordering': ['lastname', 'firstname'],
                'db_table': 'clients',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('cid', models.AutoField(serialize=False, primary_key=True)),
                ('comment', models.TextField()),
                ('add_date_time', models.DateTimeField(null=True, blank=True)),
                ('username', models.CharField(max_length=32)),
            ],
            options={
                'ordering': ['add_date_time'],
                'db_table': 'comments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('did', models.AutoField(serialize=False, primary_key=True)),
                ('filename', models.CharField(max_length=128, blank=True)),
                ('title', models.CharField(max_length=128, blank=True)),
                ('type', models.CharField(max_length=8, blank=True)),
                ('url', models.CharField(max_length=256, blank=True)),
                ('description', models.TextField(blank=True)),
                ('version', models.CharField(max_length=16, blank=True)),
                ('last_mod', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'documents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Events',
            fields=[
                ('eid', models.AutoField(serialize=False, primary_key=True)),
                ('status', models.CharField(max_length=32)),
                ('event_date_time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ['event_date_time'],
                'db_table': 'events',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comment',
            name='event',
            field=models.ForeignKey(db_column='event', blank=True, to='main.Events', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='InGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'in_group',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('iid', models.AutoField(serialize=False, primary_key=True)),
                ('type', models.CharField(max_length=12, choices=[('bug', 'bug'), ('action item', 'action item')])),
                ('title', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=16, choices=[('OPEN', 'OPEN'), ('INPROGRESS', 'IN PROGRESS'), ('RESOLVED', 'RESOLVED'), ('VERIFIED', 'VERIFIED')])),
                ('description', models.TextField(blank=True)),
                ('priority', models.IntegerField(blank=True, null=True, choices=[(0, 'ICING'), (1, 'LOW'), (2, 'MEDIUM'), (3, 'HIGH'), (4, 'CRITICAL')])),
                ('r_status', models.CharField(max_length=16, blank=True)),
                ('last_mod', models.DateTimeField(null=True, blank=True)),
                ('target_date', models.DateField(null=True, blank=True)),
                ('estimated_time', models.DurationField(null=True, blank=True)),
                ('url', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'db_table': 'items',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='events',
            name='item',
            field=models.ForeignKey(to='main.Item', db_column='item', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='item',
            field=models.ForeignKey(db_column='item', blank=True, to='main.Item', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attachment',
            name='item',
            field=models.ForeignKey(to='main.Item', db_column='item_id', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actualtime',
            name='item',
            field=models.ForeignKey(to='main.Item', db_column='iid', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ItemClient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('client', models.ForeignKey(to='main.Client', on_delete=models.CASCADE)),
                ('item', models.ForeignKey(to='main.Item', db_column='iid', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'item_clients',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('mid', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('target_date', models.DateField()),
                ('status', models.CharField(default='OPEN', max_length=8)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['target_date', 'name'],
                'db_table': 'milestones',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item',
            name='milestone',
            field=models.ForeignKey(to='main.Milestone', db_column='mid', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('nid', models.AutoField(serialize=False, primary_key=True)),
                ('subject', models.CharField(max_length=256, blank=True)),
                ('body', models.TextField(blank=True)),
                ('reply_to', models.IntegerField(null=True, blank=True)),
                ('replies', models.IntegerField(null=True, blank=True)),
                ('type', models.CharField(max_length=8)),
                ('overflow', models.BooleanField(default=False)),
                ('added', models.DateTimeField()),
                ('modified', models.DateTimeField()),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'ordering': ['-modified'],
                'db_table': 'nodes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notify',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.ForeignKey(to='main.Item', db_column='iid', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'notify',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NotifyProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'notify_project',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('pid', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('pub_view', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(max_length=16, blank=True)),
                ('type', models.CharField(max_length=50, blank=True)),
                ('area', models.CharField(max_length=100, blank=True)),
                ('url', models.CharField(max_length=255, blank=True)),
                ('restricted', models.CharField(max_length=10, blank=True)),
                ('approach', models.CharField(max_length=50, blank=True)),
                ('info_url', models.CharField(max_length=255, blank=True)),
                ('entry_rel', models.BooleanField(default=False)),
                ('eval_url', models.CharField(max_length=255, blank=True)),
                ('projnum', models.IntegerField(null=True, blank=True)),
                ('scale', models.CharField(max_length=20, blank=True)),
                ('distrib', models.CharField(max_length=20, blank=True)),
                ('poster', models.BooleanField(default=False)),
                ('wiki_category', models.CharField(max_length=256, blank=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'projects',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='notifyproject',
            name='pid',
            field=models.ForeignKey(to='main.Project', db_column='pid', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='project',
            field=models.ForeignKey(db_column='project', to='main.Project', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='milestone',
            name='project',
            field=models.ForeignKey(to='main.Project', db_column='pid', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='pid',
            field=models.ForeignKey(to='main.Project', db_column='pid', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ProjectClient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=255, blank=True)),
                ('client', models.ForeignKey(to='main.Client', on_delete=models.CASCADE)),
                ('pid', models.ForeignKey(to='main.Project', db_column='pid', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'project_clients',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatusUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('body', models.TextField(default='', blank=True)),
                ('project', models.ForeignKey(to='main.Project', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-added'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('username', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('fullname', models.CharField(max_length=128, blank=True)),
                ('email', models.CharField(max_length=32)),
                ('status', models.CharField(max_length=16, blank=True)),
                ('grp', models.BooleanField(default=False)),
                ('password', models.CharField(max_length=256, blank=True)),
                ('type', models.TextField(blank=True)),
                ('title', models.TextField(blank=True)),
                ('phone', models.TextField(blank=True)),
                ('bio', models.TextField(blank=True)),
                ('photo_url', models.TextField(blank=True)),
                ('photo_width', models.IntegerField(null=True, blank=True)),
                ('photo_height', models.IntegerField(null=True, blank=True)),
                ('campus', models.TextField(blank=True)),
                ('building', models.TextField(blank=True)),
                ('room', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['fullname'],
                'db_table': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='statusupdate',
            name='user',
            field=models.ForeignKey(to='main.User', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='caretaker',
            field=models.ForeignKey(to='main.User', db_column='caretaker', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notifyproject',
            name='username',
            field=models.ForeignKey(to='main.User', db_column='username', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notify',
            name='username',
            field=models.ForeignKey(to='main.User', db_column='username', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='notify',
            unique_together=set([('item', 'username')]),
        ),
        migrations.AddField(
            model_name='node',
            name='author',
            field=models.ForeignKey(to='main.User', db_column='author', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='owner',
            field=models.ForeignKey(to='main.User', db_column='owner', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='assigned_to',
            field=models.ForeignKey(to='main.User', db_column='assigned_to', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingroup',
            name='username',
            field=models.ForeignKey(db_column='username', blank=True, to='main.User', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingroup',
            name='grp',
            field=models.ForeignKey(to='main.User', db_column='grp', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='author',
            field=models.ForeignKey(to='main.User', db_column='author', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='client',
            name='contact',
            field=models.ForeignKey(db_column='contact', blank=True, to='main.User', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attachment',
            name='author',
            field=models.ForeignKey(to='main.User', db_column='author', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actualtime',
            name='resolver',
            field=models.ForeignKey(to='main.User', db_column='resolver', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='WorksOn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('auth', models.CharField(max_length=16)),
                ('project', models.ForeignKey(to='main.Project', db_column='pid', on_delete=models.CASCADE)),
                ('username', models.ForeignKey(to='main.User', db_column='username', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'works_on',
            },
            bases=(models.Model,),
        ),
    ]

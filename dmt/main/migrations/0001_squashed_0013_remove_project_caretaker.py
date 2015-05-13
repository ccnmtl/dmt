# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import interval.fields
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    replaces = [(b'main', '0001_initial'), (b'main', '0002_auto_20141219_1741'), (b'main', '0003_auto_20141219_1745'), (b'main', '0004_userprofile_user'), (b'main', '0005_auto_20150120_0750'), (b'main', '0006_remove_userprofile_password'), (b'main', '0007_userprofile_primary_group'), (b'main', '0008_auto_20150122_0711'), (b'main', '0009_auto_20150123_0904'), (b'main', '0010_auto_20150126_0732'), (b'main', '0011_auto_20150206_1048'), (b'main', '0012_auto_20150309_0838'), (b'main', '0013_remove_project_caretaker')]

    dependencies = [
        ('taggit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActualTime',
            fields=[
                ('actual_time', interval.fields.IntervalField(null=True, blank=True)),
                ('completed', models.DateTimeField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'actual_times',
            },
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
                'ordering': [b'lastname', b'firstname'],
                'db_table': 'clients',
            },
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
                'ordering': [b'add_date_time'],
                'db_table': 'comments',
            },
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
        ),
        migrations.CreateModel(
            name='Events',
            fields=[
                ('eid', models.AutoField(serialize=False, primary_key=True)),
                ('status', models.CharField(max_length=32)),
                ('event_date_time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': [b'event_date_time'],
                'db_table': 'events',
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='event',
            field=models.ForeignKey(db_column=b'event', blank=True, to='main.Events', null=True),
        ),
        migrations.CreateModel(
            name='InGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'in_group',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('iid', models.AutoField(serialize=False, primary_key=True)),
                ('type', models.CharField(max_length=12, choices=[(b'bug', b'bug'), (b'action item', b'action item')])),
                ('title', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=16, choices=[(b'OPEN', b'OPEN'), (b'INPROGRESS', b'IN PROGRESS'), (b'RESOLVED', b'RESOLVED'), (b'VERIFIED', b'VERIFIED')])),
                ('description', models.TextField(blank=True)),
                ('priority', models.IntegerField(blank=True, null=True, choices=[(0, b'ICING'), (1, b'LOW'), (2, b'MEDIUM'), (3, b'HIGH'), (4, b'CRITICAL')])),
                ('r_status', models.CharField(max_length=16, blank=True)),
                ('last_mod', models.DateTimeField(null=True, blank=True)),
                ('target_date', models.DateField(null=True, blank=True)),
                ('estimated_time', interval.fields.IntervalField(null=True, blank=True)),
                ('url', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'db_table': 'items',
            },
        ),
        migrations.AddField(
            model_name='events',
            name='item',
            field=models.ForeignKey(to='main.Item', db_column=b'item'),
        ),
        migrations.AddField(
            model_name='comment',
            name='item',
            field=models.ForeignKey(db_column=b'item', blank=True, to='main.Item', null=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='item',
            field=models.ForeignKey(to='main.Item', db_column=b'item_id'),
        ),
        migrations.AddField(
            model_name='actualtime',
            name='item',
            field=models.ForeignKey(to='main.Item', db_column=b'iid'),
        ),
        migrations.CreateModel(
            name='ItemClient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('client', models.ForeignKey(to='main.Client')),
                ('item', models.ForeignKey(to='main.Item', db_column=b'iid')),
            ],
            options={
                'db_table': 'item_clients',
            },
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('mid', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('target_date', models.DateField()),
                ('status', models.CharField(default=b'OPEN', max_length=8)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': [b'target_date', b'name'],
                'db_table': 'milestones',
            },
        ),
        migrations.AddField(
            model_name='item',
            name='milestone',
            field=models.ForeignKey(to='main.Milestone', db_column=b'mid'),
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
                'ordering': [b'-modified'],
                'db_table': 'nodes',
            },
        ),
        migrations.CreateModel(
            name='Notify',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.ForeignKey(to='main.Item', db_column=b'iid')),
            ],
            options={
                'db_table': 'notify',
            },
        ),
        migrations.CreateModel(
            name='NotifyProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'notify_project',
            },
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
                'ordering': [b'name'],
                'db_table': 'projects',
            },
        ),
        migrations.AddField(
            model_name='notifyproject',
            name='pid',
            field=models.ForeignKey(to='main.Project', db_column=b'pid'),
        ),
        migrations.AddField(
            model_name='node',
            name='project',
            field=models.ForeignKey(db_column=b'project', to='main.Project', null=True),
        ),
        migrations.AddField(
            model_name='milestone',
            name='project',
            field=models.ForeignKey(to='main.Project', db_column=b'pid'),
        ),
        migrations.AddField(
            model_name='document',
            name='pid',
            field=models.ForeignKey(to='main.Project', db_column=b'pid'),
        ),
        migrations.CreateModel(
            name='ProjectClient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=255, blank=True)),
                ('client', models.ForeignKey(to='main.Client')),
                ('pid', models.ForeignKey(to='main.Project', db_column=b'pid')),
            ],
            options={
                'db_table': 'project_clients',
            },
        ),
        migrations.CreateModel(
            name='StatusUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('body', models.TextField(default='', blank=True)),
                ('project', models.ForeignKey(to='main.Project')),
            ],
            options={
                'ordering': [b'-added'],
            },
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
                'ordering': [b'fullname'],
                'db_table': 'users',
            },
        ),
        migrations.AddField(
            model_name='statusupdate',
            name='user',
            field=models.ForeignKey(to='main.User'),
        ),
        migrations.AddField(
            model_name='project',
            name='caretaker',
            field=models.ForeignKey(to='main.User', db_column=b'caretaker'),
        ),
        migrations.AddField(
            model_name='notifyproject',
            name='username',
            field=models.ForeignKey(to='main.User', db_column=b'username'),
        ),
        migrations.AddField(
            model_name='notify',
            name='username',
            field=models.ForeignKey(to='main.User', db_column=b'username'),
        ),
        migrations.AlterUniqueTogether(
            name='notify',
            unique_together=set([(b'item', b'username')]),
        ),
        migrations.AddField(
            model_name='node',
            name='author',
            field=models.ForeignKey(to='main.User', db_column=b'author'),
        ),
        migrations.AddField(
            model_name='item',
            name='owner',
            field=models.ForeignKey(to='main.User', db_column=b'owner'),
        ),
        migrations.AddField(
            model_name='item',
            name='assigned_to',
            field=models.ForeignKey(to='main.User', db_column=b'assigned_to'),
        ),
        migrations.AddField(
            model_name='ingroup',
            name='username',
            field=models.ForeignKey(db_column=b'username', blank=True, to='main.User', null=True),
        ),
        migrations.AddField(
            model_name='ingroup',
            name='grp',
            field=models.ForeignKey(to='main.User', db_column=b'grp'),
        ),
        migrations.AddField(
            model_name='document',
            name='author',
            field=models.ForeignKey(to='main.User', db_column=b'author'),
        ),
        migrations.AddField(
            model_name='client',
            name='contact',
            field=models.ForeignKey(db_column=b'contact', blank=True, to='main.User', null=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='author',
            field=models.ForeignKey(to='main.User', db_column=b'author'),
        ),
        migrations.AddField(
            model_name='actualtime',
            name='resolver',
            field=models.ForeignKey(to='main.User', db_column=b'resolver'),
        ),
        migrations.CreateModel(
            name='WorksOn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('auth', models.CharField(max_length=16)),
                ('project', models.ForeignKey(to='main.Project', db_column=b'pid')),
                ('username', models.ForeignKey(to='main.User', db_column=b'username')),
            ],
            options={
                'db_table': 'works_on',
            },
        ),
        migrations.RenameModel(
            old_name='User',
            new_name='UserProfile',
        ),
        migrations.AlterField(
            model_name='ingroup',
            name='grp',
            field=models.ForeignKey(related_name='group_members', db_column=b'grp', to='main.UserProfile'),
        ),
        migrations.AlterField(
            model_name='item',
            name='assigned_to',
            field=models.ForeignKey(related_name='assigned_items', db_column=b'assigned_to', to='main.UserProfile'),
        ),
        migrations.AlterField(
            model_name='item',
            name='owner',
            field=models.ForeignKey(related_name='owned_items', db_column=b'owner', to='main.UserProfile'),
        ),
        migrations.AlterField(
            model_name='notify',
            name='item',
            field=models.ForeignKey(related_name='notifies', db_column=b'iid', to='main.Item'),
        ),
        migrations.AlterField(
            model_name='project',
            name='area',
            field=models.CharField(max_length=100, verbose_name=b'Discipline', blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='distrib',
            field=models.CharField(max_length=20, verbose_name=b'Distribution', blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='entry_rel',
            field=models.BooleanField(default=False, verbose_name=b'Released'),
        ),
        migrations.AlterField(
            model_name='project',
            name='eval_url',
            field=models.CharField(max_length=255, verbose_name=b'Evaluation URL', blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='info_url',
            field=models.CharField(max_length=255, verbose_name=b'Information URL', blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=255, verbose_name=b'Project name'),
        ),
        migrations.AlterField(
            model_name='project',
            name='poster',
            field=models.BooleanField(default=False, verbose_name=b'Poster project'),
        ),
        migrations.AlterField(
            model_name='project',
            name='projnum',
            field=models.IntegerField(null=True, verbose_name=b'Project number', blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='pub_view',
            field=models.BooleanField(default=False, verbose_name=b'PMT View'),
        ),
        migrations.AlterField(
            model_name='project',
            name='url',
            field=models.CharField(max_length=255, verbose_name=b'Project URL', blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='password',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='primary_group',
            field=models.ForeignKey(blank=True, to='main.UserProfile', null=True),
        ),
        migrations.AddField(
            model_name='actualtime',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='assigned_user',
            field=models.ForeignKey(related_name='assigned_to', db_column=b'assigned_user', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='owner_user',
            field=models.ForeignKey(related_name='owned_items', db_column=b'owner_user', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='node',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='notify',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='notifyproject',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='caretaker_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='statusupdate',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='workson',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='status',
            field=models.CharField(db_index=True, max_length=16, choices=[(b'OPEN', b'OPEN'), (b'INPROGRESS', b'IN PROGRESS'), (b'RESOLVED', b'RESOLVED'), (b'VERIFIED', b'VERIFIED')]),
        ),
        migrations.RemoveField(
            model_name='project',
            name='caretaker',
        ),
    ]

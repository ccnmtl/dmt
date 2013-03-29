# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'users', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('grp', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('type', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('phone', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('bio', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('photo_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('photo_width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('photo_height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('campus', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('building', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('room', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('main', ['User'])

        # Adding model 'Project'
        db.create_table(u'projects', (
            ('pid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pub_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('caretaker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], db_column='caretaker')),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('area', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('restricted', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('approach', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('info_url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('entry_rel', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('eval_url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('projnum', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('scale', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('distrib', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('poster', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('wiki_category', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
        ))
        db.send_create_signal('main', ['Project'])

        # Adding model 'Document'
        db.create_table(u'documents', (
            ('did', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('pid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Project'], db_column='pid')),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=8, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], db_column='author')),
            ('last_mod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('main', ['Document'])

        # Adding model 'Milestone'
        db.create_table(u'milestones', (
            ('mid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('target_date', self.gf('django.db.models.fields.DateField')()),
            ('pid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Project'], db_column='pid')),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('main', ['Milestone'])

        # Adding model 'Item'
        db.create_table(u'items', (
            ('iid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_items', db_column='owner', to=orm['main.User'])),
            ('assigned_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assigned_items', db_column='assigned_to', to=orm['main.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Milestone'], db_column='mid')),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('r_status', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('last_mod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('target_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('estimated_time', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('url', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('main', ['Item'])

        # Adding model 'Notify'
        db.create_table(u'notify', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Item'], db_column='iid')),
            ('username', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], db_column='username')),
        ))
        db.send_create_signal('main', ['Notify'])

        # Adding model 'Client'
        db.create_table(u'clients', (
            ('client_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('registration_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('department', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('school', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('add_affiliation', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], null=True, db_column='contact', blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('email_secondary', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('phone_mobile', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('phone_other', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('website_url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('main', ['Client'])

        # Adding model 'ItemClient'
        db.create_table(u'item_clients', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Item'], db_column='iid')),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Client'])),
        ))
        db.send_create_signal('main', ['ItemClient'])

        # Adding model 'Node'
        db.create_table(u'nodes', (
            ('nid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], db_column='author')),
            ('reply_to', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('replies', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('overflow', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('added', self.gf('django.db.models.fields.DateTimeField')()),
            ('modified', self.gf('django.db.models.fields.DateTimeField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Project'], null=True)),
        ))
        db.send_create_signal('main', ['Node'])

        # Adding model 'WorksOn'
        db.create_table(u'works_on', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], db_column='username')),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Project'], db_column='pid')),
            ('auth', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('main', ['WorksOn'])

        # Adding model 'Events'
        db.create_table(u'events', (
            ('eid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('event_date_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('item', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('main', ['Events'])

        # Adding model 'NotifyProject'
        db.create_table(u'notify_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Project'], db_column='pid')),
            ('username', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], db_column='username')),
        ))
        db.send_create_signal('main', ['NotifyProject'])

        # Adding model 'InGroup'
        db.create_table(u'in_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('grp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='group_members', db_column='grp', to=orm['main.User'])),
            ('username', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], null=True, db_column='username', blank=True)),
        ))
        db.send_create_signal('main', ['InGroup'])

        # Adding model 'ProjectClient'
        db.create_table(u'project_clients', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Project'], db_column='pid')),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Client'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('main', ['ProjectClient'])

        # Adding model 'ActualTime'
        db.create_table(u'actual_times', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Item'], db_column='iid')),
            ('resolver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], db_column='resolver')),
            ('actual_time', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('completed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('main', ['ActualTime'])

        # Adding model 'Attachment'
        db.create_table(u'attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Item'], db_column='iid')),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=8, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], db_column='author')),
            ('last_mod', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('main', ['Attachment'])

        # Adding model 'Comment'
        db.create_table(u'comments', (
            ('cid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('add_date_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Item'], null=True, db_column='item', blank=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Events'], null=True, db_column='event', blank=True)),
        ))
        db.send_create_signal('main', ['Comment'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'users')

        # Deleting model 'Project'
        db.delete_table(u'projects')

        # Deleting model 'Document'
        db.delete_table(u'documents')

        # Deleting model 'Milestone'
        db.delete_table(u'milestones')

        # Deleting model 'Item'
        db.delete_table(u'items')

        # Deleting model 'Notify'
        db.delete_table(u'notify')

        # Deleting model 'Client'
        db.delete_table(u'clients')

        # Deleting model 'ItemClient'
        db.delete_table(u'item_clients')

        # Deleting model 'Node'
        db.delete_table(u'nodes')

        # Deleting model 'WorksOn'
        db.delete_table(u'works_on')

        # Deleting model 'Events'
        db.delete_table(u'events')

        # Deleting model 'NotifyProject'
        db.delete_table(u'notify_project')

        # Deleting model 'InGroup'
        db.delete_table(u'in_group')

        # Deleting model 'ProjectClient'
        db.delete_table(u'project_clients')

        # Deleting model 'ActualTime'
        db.delete_table(u'actual_times')

        # Deleting model 'Attachment'
        db.delete_table(u'attachment')

        # Deleting model 'Comment'
        db.delete_table(u'comments')


    models = {
        'main.actualtime': {
            'Meta': {'object_name': 'ActualTime', 'db_table': "u'actual_times'"},
            'actual_time': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Item']", 'db_column': "'iid'"}),
            'resolver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'db_column': "'resolver'"})
        },
        'main.attachment': {
            'Meta': {'object_name': 'Attachment', 'db_table': "u'attachment'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'db_column': "'author'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Item']", 'db_column': "'iid'"}),
            'last_mod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        'main.client': {
            'Meta': {'object_name': 'Client', 'db_table': "u'clients'"},
            'add_affiliation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'client_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'null': 'True', 'db_column': "'contact'", 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'email_secondary': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'phone_mobile': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'phone_other': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'registration_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'school': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'website_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'main.comment': {
            'Meta': {'object_name': 'Comment', 'db_table': "u'comments'"},
            'add_date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Events']", 'null': 'True', 'db_column': "'event'", 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Item']", 'null': 'True', 'db_column': "'item'", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'main.document': {
            'Meta': {'object_name': 'Document', 'db_table': "u'documents'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'db_column': "'author'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'did': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'last_mod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'pid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Project']", 'db_column': "'pid'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'})
        },
        'main.events': {
            'Meta': {'object_name': 'Events', 'db_table': "u'events'"},
            'eid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'event_date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'item': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'main.ingroup': {
            'Meta': {'object_name': 'InGroup', 'db_table': "u'in_group'"},
            'grp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_members'", 'db_column': "'grp'", 'to': "orm['main.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'username': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'null': 'True', 'db_column': "'username'", 'blank': 'True'})
        },
        'main.item': {
            'Meta': {'object_name': 'Item', 'db_table': "u'items'"},
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assigned_items'", 'db_column': "'assigned_to'", 'to': "orm['main.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'estimated_time': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'iid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'last_mod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Milestone']", 'db_column': "'mid'"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_items'", 'db_column': "'owner'", 'to': "orm['main.User']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'r_status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'target_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'url': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'main.itemclient': {
            'Meta': {'object_name': 'ItemClient', 'db_table': "u'item_clients'"},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Client']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Item']", 'db_column': "'iid'"})
        },
        'main.milestone': {
            'Meta': {'object_name': 'Milestone', 'db_table': "u'milestones'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Project']", 'db_column': "'pid'"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'target_date': ('django.db.models.fields.DateField', [], {})
        },
        'main.node': {
            'Meta': {'object_name': 'Node', 'db_table': "u'nodes'"},
            'added': ('django.db.models.fields.DateTimeField', [], {}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'db_column': "'author'"}),
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'nid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'overflow': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Project']", 'null': 'True'}),
            'replies': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reply_to': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'main.notify': {
            'Meta': {'object_name': 'Notify', 'db_table': "u'notify'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Item']", 'db_column': "'iid'"}),
            'username': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'db_column': "'username'"})
        },
        'main.notifyproject': {
            'Meta': {'object_name': 'NotifyProject', 'db_table': "u'notify_project'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Project']", 'db_column': "'pid'"}),
            'username': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'db_column': "'username'"})
        },
        'main.project': {
            'Meta': {'object_name': 'Project', 'db_table': "u'projects'"},
            'approach': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'area': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'caretaker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'db_column': "'caretaker'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distrib': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'entry_rel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'eval_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'info_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'poster': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'projnum': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pub_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'restricted': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'scale': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'wiki_category': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        'main.projectclient': {
            'Meta': {'object_name': 'ProjectClient', 'db_table': "u'project_clients'"},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Client']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Project']", 'db_column': "'pid'"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'main.user': {
            'Meta': {'object_name': 'User', 'db_table': "u'users'"},
            'bio': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'building': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'campus': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'grp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'phone': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'photo_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'photo_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'photo_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'room': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'main.workson': {
            'Meta': {'object_name': 'WorksOn', 'db_table': "u'works_on'"},
            'auth': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Project']", 'db_column': "'pid'"}),
            'username': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'db_column': "'username'"})
        }
    }

    complete_apps = ['main']

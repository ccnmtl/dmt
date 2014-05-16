# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass

    models = {
        u'main.actualtime': {
            'Meta': {'object_name': 'ActualTime', 'db_table': "u'actual_times'"},
            'actual_time': ('interval.fields.IntervalField', [], {'null': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.DateTimeField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Item']", 'db_column': "'iid'"}),
            'resolver': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']", 'db_column': "'resolver'"})
        },
        u'main.attachment': {
            'Meta': {'object_name': 'Attachment', 'db_table': "u'attachment'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']", 'db_column': "'author'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Item']", 'db_column': "'item_id'"}),
            'last_mod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        u'main.client': {
            'Meta': {'ordering': "['lastname', 'firstname']", 'object_name': 'Client', 'db_table': "u'clients'"},
            'add_affiliation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'client_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']", 'null': 'True', 'db_column': "'contact'", 'blank': 'True'}),
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
        u'main.comment': {
            'Meta': {'ordering': "['add_date_time']", 'object_name': 'Comment', 'db_table': "u'comments'"},
            'add_date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cid': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Events']", 'null': 'True', 'db_column': "'event'", 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Item']", 'null': 'True', 'db_column': "'item'", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'main.document': {
            'Meta': {'object_name': 'Document', 'db_table': "u'documents'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']", 'db_column': "'author'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'did': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'last_mod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'pid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Project']", 'db_column': "'pid'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'})
        },
        u'main.events': {
            'Meta': {'ordering': "['event_date_time']", 'object_name': 'Events', 'db_table': "u'events'"},
            'eid': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'event_date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Item']", 'db_column': "'item'"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'main.ingroup': {
            'Meta': {'object_name': 'InGroup', 'db_table': "u'in_group'"},
            'grp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_members'", 'db_column': "'grp'", 'to': u"orm['main.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'username': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']", 'null': 'True', 'db_column': "'username'", 'blank': 'True'})
        },
        u'main.item': {
            'Meta': {'object_name': 'Item', 'db_table': "u'items'"},
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assigned_items'", 'db_column': "'assigned_to'", 'to': u"orm['main.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'estimated_time': ('interval.fields.IntervalField', [], {'null': 'True', 'blank': 'True'}),
            'iid': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_mod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Milestone']", 'db_column': "'mid'"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_items'", 'db_column': "'owner'", 'to': u"orm['main.User']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'r_status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'target_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'url': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'main.itemclient': {
            'Meta': {'object_name': 'ItemClient', 'db_table': "u'item_clients'"},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Client']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Item']", 'db_column': "'iid'"})
        },
        u'main.milestone': {
            'Meta': {'ordering': "['target_date', 'name']", 'object_name': 'Milestone', 'db_table': "u'milestones'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mid': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Project']", 'db_column': "'pid'"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'OPEN'", 'max_length': '8'}),
            'target_date': ('django.db.models.fields.DateField', [], {})
        },
        u'main.node': {
            'Meta': {'ordering': "['-modified']", 'object_name': 'Node', 'db_table': "u'nodes'"},
            'added': ('django.db.models.fields.DateTimeField', [], {}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']", 'db_column': "'author'"}),
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'nid': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overflow': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Project']", 'null': 'True', 'db_column': "'project'"}),
            'replies': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reply_to': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'main.notify': {
            'Meta': {'object_name': 'Notify', 'db_table': "u'notify'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Item']", 'db_column': "'iid'"}),
            'username': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']", 'db_column': "'username'"})
        },
        u'main.notifyproject': {
            'Meta': {'object_name': 'NotifyProject', 'db_table': "u'notify_project'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Project']", 'db_column': "'pid'"}),
            'username': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']", 'db_column': "'username'"})
        },
        u'main.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project', 'db_table': "u'projects'"},
            'approach': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'area': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'caretaker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']", 'db_column': "'caretaker'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distrib': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'entry_rel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'eval_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'info_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pid': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        u'main.projectclient': {
            'Meta': {'object_name': 'ProjectClient', 'db_table': "u'project_clients'"},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Client']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Project']", 'db_column': "'pid'"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'main.statusupdate': {
            'Meta': {'ordering': "['-added']", 'object_name': 'StatusUpdate'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']"})
        },
        u'main.user': {
            'Meta': {'ordering': "['fullname']", 'object_name': 'User', 'db_table': "u'users'"},
            'bio': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'building': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'campus': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'grp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'phone': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'photo_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'photo_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'photo_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'room': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'})
        },
        u'main.workson': {
            'Meta': {'object_name': 'WorksOn', 'db_table': "u'works_on'"},
            'auth': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Project']", 'db_column': "'pid'"}),
            'username': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.User']", 'db_column': "'username'"})
        }
    }

    complete_apps = ['main']

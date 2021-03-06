# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-30 15:02
from __future__ import unicode_literals

from django.db import migrations


def backfill_comment_authors(apps, schema_editor):
    Comment = apps.get_model("main", "Comment")
    UserProfile = apps.get_model("main", "UserProfile")
    User = apps.get_model("auth", "User")

    # first, there are some old stray test comments to clear out:
    Comment.objects.filter(username='testuser2').delete()
    Comment.objects.filter(username='testuserbo').delete()

    for c in Comment.objects.filter(author=None):
        print(c.cid)
        try:
            try:
                u = UserProfile.objects.get(username=c.username)
            except UserProfile.DoesNotExist:
                u = User.objects.get(username=c.username).userprofile
            c.author = u.user
            c.save()
        except Exception as e:
            print(e)
            raise


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0055_comment_author'),
    ]

    operations = [
        migrations.RunPython(backfill_comment_authors),
    ]

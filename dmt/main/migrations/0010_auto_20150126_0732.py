# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populate_caretaker(apps, schema_editor):
    Project = apps.get_model("main", "Project")
    for project in Project.objects.all():
        if project.caretaker_user is None:
            project.caretaker_user = project.caretaker.user
            project.save()


def populate_owner_assigned(apps, schema_editor):
    Item = apps.get_model("main", "Item")
    for item in Item.objects.all():
        if item.assigned_user is None:
            item.assigned_user = item.assigned_to.user
        if item.owner_user is None:
            item.owner_user = item.owner.user
        item.save()


def populate_notify(apps, schema_editor):
    Notify = apps.get_model("main", "Notify")
    for n in Notify.objects.all():
        if n.user is None:
            n.user = n.username.user
            n.save()


def populate_client_contact(apps, schema_editor):
    Client = apps.get_model("main", "Client")
    for c in Client.objects.all():
        if c.user is None:
            c.user = c.contact.user
            c.save()


def populate_author(apps, schema_editor):
    Node = apps.get_model("main", "Node")
    for n in Node.objects.all():
        if n.user is None:
            n.user = n.author.user
            n.save()


def populate_workson(apps, schema_editor):
    WorksOn = apps.get_model("main", "WorksOn")
    for w in WorksOn.objects.all():
        if w.user is None:
            w.user = w.username.user
            w.save()


def populate_actual_time(apps, schema_editor):
    ActualTime = apps.get_model("main", "ActualTime")
    for a in ActualTime.objects.all():
        if a.user is None:
            a.user = a.resolver.user
            a.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20150123_0904'),
    ]

    operations = [
        migrations.RunPython(populate_caretaker),
        migrations.RunPython(populate_owner_assigned),
        migrations.RunPython(populate_notify),
        migrations.RunPython(populate_client_contact),
        migrations.RunPython(populate_author),
        migrations.RunPython(populate_workson),
        migrations.RunPython(populate_actual_time),
    ]

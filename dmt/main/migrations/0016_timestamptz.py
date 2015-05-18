# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import migrations


def migrate_timestamptz(tbl, col):
    """
    Alter the timestamps to timestamptz, making sure to import
    them with the proper timezone. Right now the timestamps are in
    localtime, which is America/New_York, which we can get from
    settings.TIME_ZONE.

    The resulting fields will be timestamptz, which appear as UTC
    in the psql console, which Django correctly understands. As a result,
    there's no longer strange behavior when using Django's timezone
    functionality such as USE_TZ.
    """

    # Do nothing unless we're migrating postgresql.
    if settings.DATABASES['default']['ENGINE'] != \
       'django.db.backends.postgresql_psycopg2':
        return migrations.RunPython(migrations.RunPython.noop)

    sql = "ALTER TABLE {:s} ALTER COLUMN {:s} SET DATA TYPE timestamptz " \
          "USING {:s} AT TIME ZONE '{:s}';"
    sql = sql.format(tbl, col, col, settings.TIME_ZONE)
    return migrations.RunSQL(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20150514_0600'),
    ]

    operations = [
        migrate_timestamptz('documents', 'last_mod'),
        migrate_timestamptz('items', 'last_mod'),
        migrate_timestamptz('nodes', 'added'),
        migrate_timestamptz('events', 'event_date_time'),
        migrate_timestamptz('actual_times', 'completed'),
        migrate_timestamptz('attachment', 'last_mod'),
        migrate_timestamptz('comments', 'add_date_time'),
    ]

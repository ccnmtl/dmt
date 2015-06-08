# -*- coding: utf-8 -*-
from HTMLParser import HTMLParseError
from django.db import migrations
from django.db.models import Q
import html2text


def populate_comment_src(apps, schema_editor):
    """
    Populate the "comment_src" field of comments.
    """
    Comment = apps.get_model('main', 'Comment')
    for comment in Comment.objects.filter(
            comment_src='', event_id=None).filter(~Q(comment='')):
        try:
            comment.comment_src = html2text.html2text(comment.comment)
        except (ValueError, HTMLParseError):
            # If html2text raises a ValueError or
            # HTMLParseError with one of these comments,
            # it's probably due to an invalid unicode
            # entity, so just leave the src blank. The
            # comment will continue to display in PMT
            # as usual, this just means that if the user
            # tries to edit the comment, the comment field
            # will be blank and they will have to copy it
            # over manually.
            #
            # See this github issue:
            # https://github.com/Alir3z4/html2text/issues/74
            pass
        comment.save()


def unpopulate_comment_src(apps, schema_editor):
    """
    Unpopulate the "comment_src" field of comments.
    """
    Comment = apps.get_model('main', 'Comment')
    for comment in Comment.objects.filter(
            event_id=None).filter(~Q(comment_src='')):
        comment.comment_src = ''
        comment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_comment_comment_src'),
    ]

    operations = [
        migrations.RunPython(populate_comment_src,
                             unpopulate_comment_src),
    ]

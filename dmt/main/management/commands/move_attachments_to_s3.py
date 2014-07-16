from django.core.management.base import BaseCommand
from dmt.main.models import Attachment
from dmt.main.utils import safe_basename
from django.conf import settings
import ntpath
import uuid
import boto
from boto.s3.key import Key


class Command(BaseCommand):
    def handle(self, **kwargs):
        conn = boto.connect_s3(
            settings.AWS_ACCESS_KEY,
            settings.AWS_SECRET_KEY)
        bucket = conn.get_bucket(settings.AWS_S3_UPLOAD_BUCKET)

        for a in Attachment.objects.filter(url='http://'):
            existing = (
                "/mnt/nfs/applications/dmt/attachments/%d.%s" % (a.id, a.type))
            filename = safe_basename(a.filename)
            (basename, extension) = ntpath.splitext(filename)
            # force the extension for some known cases

            now = a.last_mod
            uid = str(uuid.uuid4())
            object_name = "%04d/%02d/%02d/%02d/%s-%s%s" % (
                now.year, now.month, now.day,
                now.hour, basename, uid, extension)
            try:
                with open(existing, "rb") as t:
                    print existing, object_name
                    k = Key(bucket)
                    k.set_acl('public-read')
                    k.key = object_name
                    k.set_contents_from_file(t)
                    a.url = "https://s3.amazonaws.com/%s/%s" % (
                        settings.AWS_S3_UPLOAD_BUCKET,
                        object_name
                    )
                    a.save()
            except Exception, e:
                # some of the uploaded attachments are missing
                print "Exception: %s" % str(e)

# flake8: noqa
from settings_shared import *
from ccnmtlsettings.production import common
import os

project = 'dmt'
base = os.path.dirname(__file__)

locals().update(
    common(
        project=project,
        base=base,
        STATIC_ROOT=STATIC_ROOT,
        INSTALLED_APPS=INSTALLED_APPS,
        cloudfront="dbc5vd2wjeil7",
    ))

BASE_URL = "https://pmt.ccnmtl.columbia.edu"

INSTALLED_APPS += [
    'opbeat.contrib.django',
]

MIDDLEWARE_CLASSES.insert(0, 'opbeat.contrib.django.middleware.OpbeatAPMMiddleware')

try:
    from local_settings import *
except ImportError:
    pass

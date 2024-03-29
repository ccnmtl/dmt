# flake8: noqa
from dmt.settings_shared import *
from ctlsettings.production import common
import os

project = 'dmt'
base = os.path.dirname(__file__)

locals().update(
    common(
        project=project,
        base=base,
        s3prefix="ccnmtl",
        STATIC_ROOT=STATIC_ROOT,
        INSTALLED_APPS=INSTALLED_APPS,
        cloudfront="dbc5vd2wjeil7",
    ))

BASE_URL = "https://pmt.ctl.columbia.edu"

try:
    from dmt.local_settings import *
except ImportError:
    pass

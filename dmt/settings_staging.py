# flake8: noqa
from dmt.settings_shared import *
from ctlsettings.staging import common
import os

project = 'dmt'
base = os.path.dirname(__file__)

locals().update(
    common(
        project=project,
        base=base,
        STATIC_ROOT=STATIC_ROOT,
        INSTALLED_APPS=INSTALLED_APPS,
        cloudfront="d36erjh421b5om",
    ))

BASE_URL = "https://pmt.stage.ccnmtl.columbia.edu"

try:
    from dmt.local_settings import *
except ImportError:
    pass

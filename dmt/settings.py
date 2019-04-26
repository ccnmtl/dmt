# flake8: noqa
from dmt.settings_shared import *

try:
    from dmt.local_settings import *
except ImportError:
    pass

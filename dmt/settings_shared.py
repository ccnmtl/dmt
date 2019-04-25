# Django settings for dmt project.
import os.path
import sys

from ccnmtlsettings.shared import common
from django.contrib import messages
import urllib3.contrib.pyopenssl

# Tell urllib3 to use pyOpenSSL. Needed by python < 2.7.9
# to resolve an SNIMissingWarning.
# See:
#   https://urllib3.readthedocs.io/en/latest/user-guide.html#ssl-py2
#   https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
urllib3.contrib.pyopenssl.inject_into_urllib3()

project = 'dmt'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))

USE_TZ = True

if 'test' in sys.argv or 'jenkins' in sys.argv:
    WHITELIST_ORIGIN_URLS = (
        '.columbia.edu',
    )

PROJECT_APPS = [
    'dmt.api',
    'dmt.main',
    'dmt.report',
]

TEMPLATES[0]['OPTIONS']['context_processors'].extend([  # noqa
    'dmt.main.contextprocessors.graphite_base_processor',
    'dmt.main.contextprocessors.dashboard_graph_timespan',
])

MIDDLEWARE += [  # noqa
    'django.middleware.csrf.CsrfViewMiddleware',
]

INSTALLED_APPS += [  # noqa
    'django_extensions',
    'rest_framework',
    'taggit',
    'taggit_templatetags2',
    'bootstrap3',
    'emoji',
    'dmt.main',
    'dmt.report',
    'dmt.api',
    'oauth2_provider',
    's3sign',
    'crispy_forms',
]

DEBUG_TOOLBAR_CONFIG = {
    'INSERT_BEFORE': '<span class="djdt-insert-here">',
}

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',),

    'DEFAULT_MODEL_SERIALIZER_CLASS':
    'rest_framework.serializers.HyperlinkedModelSerializer',

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

BASE_URL = "https://localhost"

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

SERVER_EMAIL = 'pmt@mail.ctl.columbia.edu'
DEFAULT_FROM_EMAIL = SERVER_EMAIL

EMAIL_MAX_RETRIES = 10

DASHBOARD_GRAPH_TIMESPAN = '4weeks'

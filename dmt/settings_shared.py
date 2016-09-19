# Django settings for dmt project.
import djcelery
import os.path
import sys
from ccnmtlsettings.shared import common
from django.contrib import messages

project = 'dmt'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))

USE_TZ = True

if 'test' in sys.argv or 'jenkins' in sys.argv:
    CELERY_ALWAYS_EAGER = True

    WHITELIST_ORIGIN_URLS = (
        '.columbia.edu',
    )

PROJECT_APPS = [
    'dmt.api',
    'dmt.main',
    'dmt.report',
]

TEMPLATE_CONTEXT_PROCESSORS += [  # noqa
    'dmt.main.contextprocessors.graphite_base_processor',
]

MIDDLEWARE_CLASSES += [  # noqa
    'django.middleware.csrf.CsrfViewMiddleware',
]

djcelery.setup_loader()

INSTALLED_APPS += [  # noqa
    'django_extensions',
    'rest_framework',
    'taggit',
    'taggit_templatetags2',
    'djcelery',
    'bootstrap3',
    'emoji',
    'dmt.main',
    'dmt.report',
    'dmt.api',
    'behave_django',
    'oauth2_provider',
    's3sign',
    'crispy_forms',
]

DEBUG_TOOLBAR_CONFIG = {
    'INSERT_BEFORE': '<span class="djdt-insert-here">',
}

BROKER_URL = "amqp://localhost:5672//dmt"
CELERYD_CONCURRENCY = 2

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),

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

SERVER_EMAIL = 'pmt@ccnmtl.columbia.edu'
DEFAULT_FROM_EMAIL = SERVER_EMAIL

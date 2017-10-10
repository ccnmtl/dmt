# Django settings for dmt project.
import djcelery
import os.path
import sys
import zmqproxy

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
    'dmt.chat',
]

TEMPLATES[0]['OPTIONS']['context_processors'].extend([  # noqa
    'dmt.main.contextprocessors.graphite_base_processor',
    'dmt.main.contextprocessors.dashboard_graph_timespan',
])

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
    'dmt.chat',
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

SERVER_EMAIL = 'pmt@ccnmtl.columbia.edu'
DEFAULT_FROM_EMAIL = SERVER_EMAIL

EMAIL_MAX_RETRIES = 10

DASHBOARD_GRAPH_TIMESPAN = '4weeks'
BROKER_PROXY = zmqproxy.ZMQProxy
ZMQ_APPNAME = 'dmt'

WINDSOCK_BROKER_URL = "tcp://localhost:5555"
WINDSOCK_WEBSOCKETS_BASE = "ws://localhost:5050/socket/"
WINDSOCK_SECRET = "6f1d916c-7761-4874-8d5b-8f8f93d20bf2"

if 'test' in sys.argv or 'jenkins' in sys.argv:
    BROKER_PROXY = zmqproxy.DummyProxy

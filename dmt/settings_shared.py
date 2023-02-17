from __future__ import unicode_literals

# Django settings for dmt project.
import os.path
import sys

from ctlsettings.shared import common
from django.contrib import messages


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

MIDDLEWARE += [  # noqa
    'django.middleware.csrf.CsrfViewMiddleware',
    'django_cas_ng.middleware.CASMiddleware',
]

INSTALLED_APPS += [  # noqa
    'django_extensions',
    'waffle',
    'django_markwhat',
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

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend'
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(base, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'stagingcontext.staging_processor',
                'gacontext.ga_processor',
                'django.template.context_processors.csrf',
                'dmt.main.contextprocessors.graphite_base_processor',
                'dmt.main.contextprocessors.dashboard_graph_timespan',
            ],
        },
    },
]

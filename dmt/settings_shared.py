# Django settings for dmt project.
import os.path
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dmt',
        'HOST': '',
        'PORT': 5432,
        'USER': '',
        'PASSWORD': '',
    }
}

if 'test' in sys.argv or 'jenkins' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '',
        }
    }

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
SOUTH_TESTS_MIGRATE = False

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=dmt',
]

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
)
PROJECT_APPS = [
    'dmt.main',
]

ALLOWED_HOSTS = ['localhost', '.ccnmtl.columbia.edu']

USE_TZ = True
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_ROOT = "/var/www/dmt/uploads/"
MEDIA_URL = '/uploads/'
STATIC_URL = '/media/'
SECRET_KEY = ')ng#)ef_u@_^zvvu@dxm7ql-yb^_!a6%v3v^j3b(mp+)l+5%@h'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'stagingcontext.staging_processor',
)

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'waffle.middleware.WaffleMiddleware',
)

ROOT_URLCONF = 'dmt.urls'

TEMPLATE_DIRS = (
    "/var/www/dmt/templates/",
    os.path.join(os.path.dirname(__file__), "templates"),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'staticmedia',
    'sorl.thumbnail',
    'django.contrib.admin',
    'tagging',
    'typogrify',
    'munin',
    'south',
    'django_nose',
    'compressor',
    'django_statsd',
    'bootstrapform',
    'lettuce.django',
    'debug_toolbar',
    'waffle',
    'django_jenkins',
    'smoketest',
    'django_extensions',
    'impersonate',
    'dmt.main',
]

LETTUCE_APPS = (
    'dmt.main',
)

INTERNAL_IPS = ('127.0.0.1', )
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

STATSD_CLIENT = 'statsd.client'
STATSD_PREFIX = 'dmt'
STATSD_HOST = '127.0.0.1'
STATSD_PORT = 8125
STATSD_PATCHES = ['django_statsd.patches.db', ]

THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[dmt] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "dmt@ccnmtl.columbia.edu"
DEFAULT_FROM_EMAIL = SERVER_EMAIL

# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', 'sitemedia'),
)

COMPRESS_URL = "/site_media/"
COMPRESS_ROOT = "media/"

# WIND settings

AUTHENTICATION_BACKENDS = ('djangowind.auth.WindAuthBackend',
                           'django.contrib.auth.backends.ModelBackend', )
WIND_BASE = "https://wind.columbia.edu/"
WIND_SERVICE = "cnmtl_full_np"
WIND_PROFILE_HANDLERS = ['djangowind.auth.CDAPProfileHandler']
WIND_AFFIL_HANDLERS = ['djangowind.auth.AffilGroupMapper',
                       'djangowind.auth.StaffMapper',
                       'djangowind.auth.SuperuserMapper']
WIND_STAFF_MAPPER_GROUPS = ['tlc.cunix.local:columbia.edu']
WIND_SUPERUSER_MAPPER_GROUPS = ['anp8', 'jb2410', 'zm4', 'egr2107',
                                'sld2131', 'amm8', 'mar227', 'jed2161']

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
LOGIN_REDIRECT_URL = "/"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

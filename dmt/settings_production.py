# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/dmt/dmt/dmt/templates",
)

MEDIA_ROOT = '/var/www/dmt/uploads/'
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', '/var/www/dmt/dmt/sitemedia'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dmt',
        'HOST': '',
        'PORT': 6432,
        'USER': '',
        'PASSWORD': '',
    }
}

COMPRESS_ROOT = "/var/www/dmt/dmt/media/"
DEBUG = False
TEMPLATE_DEBUG = DEBUG

STATICFILES_DIRS = ()
STATIC_ROOT = "/var/www/dmt/dmt/media/"

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

try:
    from local_settings import *
except ImportError:
    pass

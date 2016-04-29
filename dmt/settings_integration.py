# flake8: noqa
from settings_shared import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ci_test',
        'HOST': '',
        'PORT': '',
        'USER': '',
        'PASSWORD': '',
        'ATOMIC_REQUESTS': True,
        }
    }

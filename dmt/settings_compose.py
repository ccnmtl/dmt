# flake8: noqa
from settings_shared import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
        'ATOMIC_REQUESTS': True,
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
BROKER_URL = "amqp://guest:guest@rabbitmq:5672/"
WINDSOCK_BROKER_URL = "tcp://broker:5555"
ZMQ_APPNAME = "dmt"
WINDSOCK_SECRET = "6f1d916c-7761-4874-8d5b-8f8f93d20bf2"
WINDSOCK_WEBSOCKETS_BASE = "ws://localhost:5050/socket/"

try:
    from local_settings import *
except ImportError:
    pass

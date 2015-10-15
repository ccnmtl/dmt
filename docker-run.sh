#!/bin/bash

cd /var/www/dmt/dmt/
python manage.py migrate --noinput --settings=dmt.settings_docker
python manage.py collectstatic --noinput --settings=dmt.settings_docker
python manage.py compress --settings=dmt.settings_docker
exec gunicorn --env \
  DJANGO_SETTINGS_MODULE=dmt.settings_docker \
  dmt.wsgi:application -b 0.0.0.0:8000 -w 3 \
  --access-logfile=- --error-logfile=-

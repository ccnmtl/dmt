#!/bin/bash

cd /var/www/dmt/dmt/
exec python manage.py celery worker --settings=dmt.settings_docker

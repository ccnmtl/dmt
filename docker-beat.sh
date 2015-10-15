#!/bin/bash

cd /var/www/dmt/dmt/
exec python manage.py celery beat --settings=dmt.settings_docker

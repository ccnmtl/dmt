#!/bin/bash

cd /app/

if [[ "$SETTINGS" ]]; then
		export DJANGO_SETTINGS_MODULE="$APP.$SETTINGS"
else
		export DJANGO_SETTINGS_MODULE="$APP.settings_docker"
fi

if [ "$1" == "migrate" ]; then
		exec /ve/bin/python manage.py migrate --noinput
fi

if [ "$1" == "collectstatic" ]; then
		exec /ve/bin/python manage.py collectstatic --noinput
fi

if [ "$1" == "shell" ]; then
		exec /ve/bin/python manage.py shell
fi

# run arbitrary commands
if [ "$1" == "manage" ]; then
		shift
		exec /ve/bin/python manage.py "$@"
fi


if [ "$1" == "run" ]; then
		exec /ve/bin/gunicorn --env \
				 DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE \
				 $APP.wsgi:application -b 0.0.0.0:8000 -w 3 \
				 --access-logfile=- --error-logfile=-
fi

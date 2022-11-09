#!/bin/sh
export DJANGO_SETTINGS_MODULE=freightmonster.settings.dev
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
gunicorn freightmonster.wsgi:application --bind 0.0.0.0:8000
#!/bin/sh
python manage.py collectstatic
python manage.py makemigrations --noinput
python manage.py migrate
gunicorn freightmonster.wsgi:application --bind 0.0.0.0:8000
#!/bin/sh
celery -A freightmonster worker --loglevel=info
celery -A freightmonster beat --loglevel=info
python manage.py crontab add
python manage.py collectstatic
python manage.py makemigrations --noinput
python manage.py migrate
gunicorn freightmonster.wsgi:application --bind 0.0.0.0:8000
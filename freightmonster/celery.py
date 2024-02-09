# celery.py
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freightmonster.settings.dev')

app = Celery('freightmonster')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Define periodic tasks
app.conf.beat_schedule = {
    'periodic-task': {
        'task': 'freightmonster.tasks.periodic_task',
        'schedule': crontab(minute='*/2'),  # Run at midnight every day
        # You can adjust the schedule as needed
    },
}

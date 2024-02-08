# tasks.py
from celery import shared_task

@shared_task
def periodic_task():
    # Your task logic here
    print("This is a periodic task")

# tasks.py
from celery import shared_task
import logging
logger = logging.getLogger(__name__)
@shared_task
def periodic_task():
    # Your task logic here
    logger.info("this is periodic task")
    print("This is a periodic task")

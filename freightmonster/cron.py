from datetime import timedelta

from django.utils import timezone

from shipment.models import Load, LoadNote
from django.db.models import Q

import logging

logger = logging.getLogger(__name__)


def delete_load_draft_after_30_days():
    thirty_days_ago = timezone.now() - timedelta(days=30)
    filter_query = (
            (Q(is_deleted=True) & Q(last_updated__lt=thirty_days_ago)) |
            (Q(is_draft=True) & Q(created_at__lt=thirty_days_ago))
    )
    loads_drafts = Load.objects.filter(filter_query)
    if loads_drafts.exists():
        loads_drafts.delete()


def test_cron():
    load_note = LoadNote.objects.get(id=115)
    if not load_note.is_deleted:
        load_note.is_deleted=True
        load_note.save()
    logger.info("deleeteted")

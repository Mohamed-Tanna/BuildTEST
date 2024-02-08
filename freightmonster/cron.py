from datetime import timedelta

from django.utils import timezone

from shipment.models import Load
from django.db.models import Q


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
    print("testing cron")

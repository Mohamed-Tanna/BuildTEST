from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from shipment.models import Load


class DeleteLoadDraftCommand(BaseCommand):
    help = 'Delete old load drafts that are older than 30 days'

    def handle(self, *args, **kwargs):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        filter_query = (
                (Q(is_deleted=True) & Q(last_updated__lt=thirty_days_ago)) |
                (Q(is_draft=True) & Q(created_at__lt=thirty_days_ago))
        )
        loads_drafts = Load.objects.filter(filter_query)
        if loads_drafts.exists():
            loads_drafts.delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted old load drafts'))

from django.db.models.signals import Signal
from django.db.models.signals import post_save
from django.dispatch import receiver

import shipment.models as models
from freightmonster.constants import CLAIM_CREATED
from notifications.utilities import handle_notification
from shipment.utilities import send_notifications_to_load_parties

load_note_attachment_confirmed = Signal()
claim_note_supporting_doc_confirmed = Signal()
claim_supporting_doc_confirmed = Signal()



@receiver(load_note_attachment_confirmed)
def handle_load_note_attachment_confirmed(sender, load_note: models.LoadNote, **kwargs):
    load_note.refresh_from_db()
    new_attachments = list(set(load_note.attachments))
    if len(new_attachments) != len(load_note.attachments):
        load_note.attachments = new_attachments
        load_note.save()


@receiver(claim_note_supporting_doc_confirmed)
def handle_claim_note_attachment_confirmed(sender, claim_note: models.ClaimNote, **kwargs):
    claim_note.refresh_from_db()
    new_supporting_docs = list(set(claim_note.supporting_docs))
    if len(new_supporting_docs) != len(claim_note.supporting_docs):
        claim_note.supporting_docs = new_supporting_docs
        claim_note.save()

@receiver(claim_supporting_doc_confirmed)
def handle_claim_attachment_confirmed(sender, claim: models.Claim, **kwargs):
    claim.refresh_from_db()
    new_supporting_docs = list(set(claim.supporting_docs))
    if len(new_supporting_docs) != len(claim.supporting_docs):
        claim.supporting_docs = new_supporting_docs
        claim.save()


@receiver(post_save, sender=models.Load)
def add_to_load_notification_handler(sender, instance: models.Load, created, **kwargs):
    if created and not instance.is_draft:
        send_notifications_to_load_parties(
            load=instance, action="add_to_load", event="load_created"
        )


@receiver(post_save, sender=models.Claim)
def add_to_load_notification_handler(sender, instance: models.Claim, created, **kwargs):
    if created:
        send_notifications_to_load_parties(
            load=instance.load, action=CLAIM_CREATED, event=CLAIM_CREATED, claim=instance
        )


@receiver(post_save, sender=models.ShipmentAdmin)
def add_to_shipment_admin_notification_handler(
        sender, instance: models.ShipmentAdmin, created, **kwargs
):
    if created:
        shipment = models.Shipment.objects.get(id=instance.shipment.id)
        handle_notification(
            action="add_as_shipment_admin",
            app_user=instance.admin,
            sender=shipment.created_by,
            shipment=shipment,
        )


@receiver(post_save, sender=models.Contact)
def add_as_contact_notification_handler(
        sender, instance: models.Contact, created, **kwargs
):
    if created:
        origin = models.AppUser.objects.get(user=instance.origin)
        handle_notification(
            action="add_as_contact", app_user=instance.contact, sender=origin
        )


@receiver(post_save, sender=models.Offer)
def offer_notification_handler(sender, instance: models.Offer, created, **kwargs):
    if created and instance.party_1.app_user != instance.party_2:
        handle_notification(
            action="got_offer",
            app_user=instance.party_2,
            load=instance.load,
            sender=instance.party_1.app_user,
        )

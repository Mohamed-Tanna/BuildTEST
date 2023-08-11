from django.db.models.signals import post_save
from django.dispatch import receiver
import shipment.models as models
from shipment.utilities import send_notifications_to_load_parties
from notifications.utilities import handle_notification

@receiver(post_save, sender=models.Load)
def add_to_load_notification_handler(sender, instance: models.Load, created, **kwargs):
    if created:
        send_notifications_to_load_parties(load=instance, action="add_to_load", event="load_created")
            

@receiver(post_save, sender=models.ShipmentAdmin)
def add_to_shipment_admin_notification_handler(sender, instance: models.ShipmentAdmin, created, **kwargs):
    if created:
        shipment = models.Shipment.objects.get(id=instance.shipment.id)
        handle_notification(action="add_as_shipment_admin", app_user=instance.admin, sender=shipment.created_by, shipment=shipment)


@receiver(post_save, sender=models.Contact)
def add_as_contact_notification_handler(sender, instance: models.Contact, created, **kwargs):
    if created:
        origin = models.AppUser.objects.get(user=instance.origin)
        handle_notification(action="add_as_contact", app_user=instance.contact, sender=origin)


@receiver(post_save, sender=models.Offer)
def offer_notification_handler(sender, instance: models.Offer, created, **kwargs):
    if created:
        handle_notification(action="got_offer", app_user=instance.party_2, load=instance.load, sender=instance.party_1.app_user)
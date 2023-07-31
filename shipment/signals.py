from django.db.models.signals import post_save
from django.dispatch import receiver
import shipment.models as models
from notifications.utilities import handle_notification

@receiver(post_save, sender=models.Load)
def add_to_load_notification_handler(sender, instance: models.Load, created, **kwargs):
    if created:
        notified_usernames = set()
        roles = ['dispatcher', 'shipper', 'consignee', 'customer']

        for role in roles:
            app_user = getattr(instance, role).app_user
            username = app_user.user.username

            if username not in notified_usernames:
                handle_notification(action="add_to_load", app_user=app_user, load=instance)
                notified_usernames.add(username)
            

@receiver(post_save, sender=models.ShipmentAdmin)
def add_to_shipment_admin_notification_handler(sender, instance: models.ShipmentAdmin, created, **kwargs):
    if created:
        handle_notification(action="add_as_shipment_admin", app_user=instance.admin, shipment=instance.shipment)


@receiver(post_save, sender=models.Contact)
def add_as_contact_notification_handler(sender, instance: models.Contact, created, **kwargs):
    if created:
        handle_notification(action="add_as_contact", app_user=instance.contact)


@receiver(post_save, sender=models.Offer)
def offer_notification_handler(sender, instance: models.Offer, created, **kwargs):
    if created:
        handle_notification(action="got_offer", app_user=instance.party_2, load=instance.load)
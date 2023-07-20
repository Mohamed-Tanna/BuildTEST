from django.db import models
from authentication.models import AppUser


class Notification(models.Model):
    user = models.OneToOneField(to=AppUser, on_delete=models.CASCADE, null=False)
    message = models.TextField(null=False)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class NotificationSetting(models.Model):
    user = models.OneToOneField(to=AppUser, on_delete=models.CASCADE, null=False)
    is_allowed = models.BooleanField(default=True)
    methods = models.CharField(
        choices=[("email", "email"), ("sms", "sms"), ("both", "both"), ("none", "none")],
        default="email",
        max_length=5,
    )
    add_as_contact = models.BooleanField(default=True)
    add_to_load = models.BooleanField(default=True)
    got_offer = models.BooleanField(default=True)
    offer_updated = models.BooleanField(default=True)
    add_as_shipment_admin = models.BooleanField(default=True)
    load_to_ready_to_pickup = models.BooleanField(default=True)
    load_to_in_transit = models.BooleanField(default=True)
    load_to_delivered = models.BooleanField(default=True)
    load_to_canceled = models.BooleanField(default=True)
    RC_approved = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

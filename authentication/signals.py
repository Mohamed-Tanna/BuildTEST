from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import AppUser
from rolepermissions.roles import assign_role, get_user_roles
from .roles import *


@receiver(post_save, sender=User)
def create_user_role(sender, instance, created, **kwargs):
    if created:
        assign_role(instance, UserRole)

@receiver(post_save, sender=AppUser)
def create_app_user_role(sender, instance, created, **kwargs):
    if created:
        assign_role(instance, AppUserRole)
        if instance.user_type == "carrier":
            assign_role(instance, CarrierRole)
        elif instance.user_type == "broker":
            assign_role(instance, BrokerRole)
        elif instance.user_type == "shipment party":
            assign_role(instance, ShipmentPartyRole)
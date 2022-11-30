from email.policy import default
from django.db import models
from django.contrib.auth.models import User


class AppUser(models.Model):

    user = models.OneToOneField(to=User, null=False, unique=True, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=18, unique=True) #nullable
    user_type = models.CharField(
        choices=[
            ("carrier", "carrier"),
            ("broker", "broker"),
            ("shipment party", "shipment party"),
        ],
        max_length=14,
        null=False,
    )
    is_deleted = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return self.user.username


class Broker(models.Model):

    app_user = models.OneToOneField(
        to=AppUser,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )
    MC_number = models.CharField(max_length=8, null=False, blank=False)
    allowed_to_operate = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.app_user.user.username


class Carrier(models.Model):

    app_user = models.OneToOneField(to=AppUser, null=False, blank=False, on_delete=models.CASCADE)
    DOT_number = models.CharField(max_length=8, null=False, blank=False)
    MC_number = models.CharField(max_length=8, null=True)
    allowed_to_operate = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.app_user.user.username
    

class ShipmentParty(models.Model):

    app_user = models.OneToOneField(to=AppUser, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.app_user.user.username



from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

SHIPMENT_PARTY = "shipment party"

class AppUser(models.Model):

    user = models.OneToOneField(
        to=User,
        null=False,
        unique=True,
        on_delete=models.CASCADE,
    )
    phone_number = models.CharField(max_length=18, unique=True)  # nullable
    user_type = models.CharField(
        choices=[
            ("carrier", "carrier"),
            ("broker", "broker"),
            (SHIPMENT_PARTY, SHIPMENT_PARTY),
            ("broker-carrier", "broker-carrier"),
            (f"broker-{SHIPMENT_PARTY}", f"broker-{SHIPMENT_PARTY}"),
            (f"carrier-{SHIPMENT_PARTY}", f"carrier-{SHIPMENT_PARTY}"),
            (f"broker-carrier-{SHIPMENT_PARTY}", f"broker-carrier-{SHIPMENT_PARTY}"),
        ],
        max_length=29,
        null=False,
    )
    selected_role = models.CharField(
        choices=[
            ("carrier", "carrier"),
            ("broker", "broker"),
            (SHIPMENT_PARTY, SHIPMENT_PARTY),
        ],
        max_length=14,
        null=False,
    )

    def __str__(self):
        return self.user.username


class Broker(models.Model):

    app_user = models.OneToOneField(
        to=AppUser,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    MC_number = models.CharField(max_length=8, null=False, blank=False)
    allowed_to_operate = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.app_user.user.username


class Carrier(models.Model):

    app_user = models.OneToOneField(
        to=AppUser,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    DOT_number = models.CharField(max_length=8, null=False, blank=False)
    allowed_to_operate = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.app_user.user.username


class ShipmentParty(models.Model):

    app_user = models.OneToOneField(
        to=AppUser,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.app_user.user.username


class Address(models.Model):
    created_by = models.ForeignKey(to=AppUser, null=False, blank=False, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=False, blank=False)
    city = models.CharField(max_length=100, null=False, blank=False)
    state = models.CharField(max_length=100, null=False, blank=False)
    zip_code = models.CharField(max_length=100, null=False, blank=False)
    country = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.country}"


class Company(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)
    identifier = models.CharField(max_length=10, null=False, blank=False, unique=True)
    EIN = models.CharField(
        max_length=9,
        null=False,
        blank=False,
        unique=True,
        validators=[MinLengthValidator(9)],
    )
    address = models.OneToOneField(
        to=Address, null=False, blank=False, on_delete=models.CASCADE
    )
    fax_number = models.CharField(max_length=18, default="N/A")
    phone_number = models.CharField(max_length=18, null=False, blank=False)

    def __str__(self):
        return self.name


class CompanyEmployee(models.Model):
    app_user = models.OneToOneField(
        to=AppUser, null=False, blank=False, unique=True, on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        to=Company, null=False, blank=False, on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (("app_user", "company"),)


class UserTax(models.Model):
    app_user = models.OneToOneField(
        to=AppUser, null=False, blank=False, on_delete=models.CASCADE
    )
    TIN = models.CharField(
        max_length=9,
        null=False,
        blank=False,
        unique=True,
        validators=[MinLengthValidator(9)],
    )
    address = models.OneToOneField(to=Address, null=False, blank=False, on_delete=models.CASCADE)
    
    
class Invitation(models.Model):
    inviter = models.ForeignKey(User, on_delete=models.CASCADE)
    invitee = models.EmailField()
    token = models.UUIDField(unique=True, null=False, blank=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__ (self):
        return f"{self.inviter} invited {self.invitee} at {self.created_at}"
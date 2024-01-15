from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.contrib.postgres.fields import ArrayField
from authentication.models import (
    User,
    AppUser,
    ShipmentParty,
    Dispatcher,
    Carrier,
    Address,
)


class Facility(models.Model):
    owner = models.ForeignKey(
        to=User, null=False, blank=False, on_delete=models.CASCADE
    )
    building_name = models.CharField(max_length=100, null=False, blank=False)
    address = models.OneToOneField(
        to=Address, null=False, blank=False, on_delete=models.CASCADE
    )
    extra_info = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.owner.username} => {self.building_name}"


class Trailer(models.Model):
    model = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    max_height = models.FloatField()
    max_length = models.FloatField()
    max_width = models.FloatField()


class Shipment(models.Model):
    created_by = models.ForeignKey(
        to=AppUser, null=False, on_delete=models.CASCADE, related_name="customer"
    )
    name = models.CharField(max_length=100, null=False, unique=True)

    class Meta:
        unique_together = (("created_by", "name"),)

    def __str__(self):
        return self.name


class Load(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(to=AppUser, null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    customer = models.ForeignKey(
        to=ShipmentParty,
        null=False,
        on_delete=models.CASCADE,
        related_name="customer",
    )
    shipper = models.ForeignKey(
        to=ShipmentParty,
        null=False,
        on_delete=models.CASCADE,
        related_name="shipper",
    )
    consignee = models.ForeignKey(
        to=ShipmentParty,
        null=False,
        on_delete=models.CASCADE,
        related_name="consignee",
    )
    dispatcher = models.ForeignKey(
        to=Dispatcher, null=False, blank=False, on_delete=models.CASCADE
    )
    carrier = models.ForeignKey(to=Carrier, null=True, on_delete=models.CASCADE)
    pick_up_date = models.DateField(null=False)
    delivery_date = models.DateField(null=False)
    pick_up_location = models.ForeignKey(
        to=Facility, on_delete=models.CASCADE, related_name="pick_up"
    )
    destination = models.ForeignKey(
        to=Facility, on_delete=models.CASCADE, related_name="destination"
    )
    length = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    width = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    height = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    weight = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    commodity = models.CharField(max_length=255, null=False, blank=False)
    equipment = models.CharField(max_length=255, null=False, blank=False)
    goods_info = models.CharField(
        choices=[("Yes", "Yes"), ("No", "No")], max_length=3, null=False, default="No"
    )  # Hazardous materials
    load_type = models.CharField(
        choices=[("LTL", "LTL"), ("FTL", "FTL")],
        max_length=3,
        null=False,
        default="FTL",
    )
    status = models.CharField(
        choices=[
            ("Created", "Created"),
            ("Awaiting Customer", "Awaiting Customer"),
            ("Assigning Carrier", "Assigning Carrier"),
            ("Awaiting Carrier", "Awaiting Carrier"),
            ("Awaiting Dispatcher", "Awaiting Dispatcher"),
            ("Ready For Pickup", "Ready For Pickup"),
            ("In Transit", "In Transit"),
            ("Delivered", "Delivered"),
            ("Canceled", "Canceled"),
        ],
        max_length=20,
        null=False,
        default="Created",
    )

    shipment = models.ForeignKey(to=Shipment, null=False, on_delete=models.CASCADE)
    actual_delivery_date = models.DateField(null=True)

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(delivery_date__gt=F("pick_up_date")),
                name="delivery_date_check",
            ),
            CheckConstraint(
                check=~Q(pick_up_location=F("destination")),
                name="pick up location and drop off location cannot be equal",
            ),
        ]

    def __str__(self):
        return self.name


class Contact(models.Model):
    origin = models.ForeignKey(
        to=User, null=True, on_delete=models.CASCADE, related_name="main"
    )
    contact = models.ForeignKey(
        to=AppUser, null=True, on_delete=models.CASCADE, related_name="contact"
    )

    class Meta:
        unique_together = (("origin", "contact"),)


class Offer(models.Model):
    party_1 = models.ForeignKey(
        to=Dispatcher, null=False, on_delete=models.CASCADE, related_name="bidder"
    )
    party_2 = models.ForeignKey(
        to=AppUser, null=False, on_delete=models.CASCADE, related_name="receiver"
    )
    initial = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    current = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    status = models.CharField(
        null=False,
        choices=[
            ("Accepted", "Accepted"),
            ("Rejected", "Rejected"),
            ("Pending", "Pending"),
        ],
        max_length=8,
        default="Pending",
    )
    load = models.ForeignKey(to=Load, null=False, on_delete=models.CASCADE)
    to = models.CharField(
        null=False,
        choices=[("customer", "customer"), ("carrier", "carrier")],
        max_length=8,
        default="customer",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("party_1", "party_2", "load", "to"),)


class ShipmentAdmin(models.Model):
    shipment = models.ForeignKey(to=Shipment, null=False, on_delete=models.CASCADE)
    admin = models.ForeignKey(to=AppUser, null=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("shipment", "admin"),)


class Claim(models.Model):
    load = models.OneToOneField(to=Load, on_delete=models.CASCADE)
    claimant = models.ForeignKey(
        to=AppUser,
        related_name='claim_claimant',
        null=False,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        null=False,
        blank=False,
        choices=[
            ("open", "open"),
            ("resolved", "resolved"),
        ],
        max_length=11,
    )
    description_of_loss = models.TextField(blank=True, null=False)
    supporting_docs = ArrayField(models.TextField(), null=False, blank=True)
    date_of_loss = models.DateField(null=False)


class ClaimNote(models.Model):
    claim = models.ForeignKey(to=Claim, on_delete=models.CASCADE)
    creator = models.ForeignKey(to=AppUser, on_delete=models.CASCADE)
    message = models.TextField(
        blank=False,
        null=False
    )
    supporting_docs = ArrayField(models.TextField(), null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('claim', 'creator')

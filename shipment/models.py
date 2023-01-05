from datetime import date
from django.db import models
from django.db.models import CheckConstraint, Q, F
from authentication.models import *


class Facility(models.Model):

    owner = models.ForeignKey(
        to=User, null=False, blank=False, on_delete=models.CASCADE
    )
    building_number = models.CharField(max_length=100)
    building_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
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
    created_by = models.ForeignKey(to=AppUser, null=False, on_delete=models.CASCADE, related_name="customer")
    name = models.CharField(max_length=100, null=False)
    status = models.CharField(
        choices=[
            ("Created", "Created"),
            ("Signed", "Signed"),
            ("Completed", "Completed"),
            ("Canceled", "Canceled"),
        ],
        max_length=20,
        null=False,
        default="Created",
    )

    class Meta:
        unique_together = (("created_by", "name"),)


class Load(models.Model):

    created_by = models.ForeignKey(to=AppUser, null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=False, null=False, blank=False)
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
    broker = models.ForeignKey(to=Broker, null=True, on_delete=models.CASCADE)
    carrier = models.ForeignKey(to=Carrier, null=True, on_delete=models.CASCADE)
    pick_up_date = models.DateField(null=False)
    delivery_date = models.DateField(null=False)
    pick_up_location = models.ForeignKey(
        to=Facility, on_delete=models.CASCADE, related_name="pick_up"
    )
    destination = models.ForeignKey(
        to=Facility, on_delete=models.CASCADE, related_name="destination"
    )
    height = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    width = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    depth = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    weight = models.DecimalField(max_digits=12, decimal_places=4, null=False)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    goods_info = models.TextField(null=True)
    load_type = models.CharField(
        choices=[("LTL", "LTL"), ("FTL", "FTL")],
        max_length=3,
        null=False,
        default="FTL",
    )
    did_shipper_sign = models.BooleanField(default=False)
    did_carrier_sign = models.BooleanField(default=False)
    status = models.CharField(
        choices=[
            ("Created", "Created"),
            ("Awaiting shipper", "Awaiting shipper"),
            ("Awaiting carrier", "Awaiting carrier"),
            ("Ready For Pick Up", "Ready For Pick Up"),
            ("In Transit", "In Transit"),
            ("Delivered", "Delivered"),
            ("Canceled", "Canceled"),
        ],
        max_length=20,
        null=False,
        default="Created",
    )
    shipment = models.ForeignKey(to=Shipment, null=False, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(delivery_date__gt=F("pick_up_date")),
                name="delivery_date_check",
            ),
            CheckConstraint(
                check=Q(pick_up_date__gte=date.today()),
                name="pick_up_date should be greater than or equal today's date",
            ),
            CheckConstraint(
                check=~Q(pick_up_location=F("destination")),
                name="pick up location and drop off location cannot be equal",
            ),
        ]


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
    party_1 = models.ForeignKey(to=Broker, null=False, on_delete=models.CASCADE, related_name="bidder")
    party_2 = models.ForeignKey(to=AppUser, null=False, on_delete=models.CASCADE, related_name="receiver")
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


class ShipmentAdmin(models.Model):
    shipment = models.ForeignKey(to=Shipment, null=False, on_delete=models.CASCADE)
    admin = models.ForeignKey(to=AppUser, null=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("shipment", "admin"),)